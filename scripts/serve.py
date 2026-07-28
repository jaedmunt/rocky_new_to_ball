#!/usr/bin/env python3
"""
serve.py — minimal OpenAI-compatible chat server for grug-3b (Nanbeige arch).

sglang / vllm don't have a Nanbeige model class, and grug-3b ships its own
`modeling_nanbeige.py` that requires `trust_remote_code=True`. So we serve it
with plain transformers behind a tiny FastAPI app that speaks the subset of
the OpenAI Chat Completions API a client like llm-tui-rs needs.

Endpoints:
  GET  /v1/models
  POST /v1/chat/completions           (streaming when "stream": true)

Run:
  uv run --python grug-env-win python scripts/serve.py \
      --model-path ./models/grug-3b/model --port 67
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from threading import Thread
from typing import Any

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

REPO = Path(__file__).resolve().parent.parent
UI_INDEX = REPO / "ui" / "index.html"
SYSTEM_PROMPT_FILE = REPO / "data" / "processed" / "system_prompt.md"

import re as _re
_SAFE_NAME = _re.compile(r"[^A-Za-z0-9 _\-'.]")

def _sanitize_name(raw: str | None, fallback: str = "Grace") -> str:
    if not raw:
        return fallback
    cleaned = _SAFE_NAME.sub("", raw).strip()[:20]
    return cleaned or fallback

def _load_system_prompt(user_name: str) -> str:
    if not SYSTEM_PROMPT_FILE.exists():
        return ""
    return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").replace("{name}", user_name)

sys.path.insert(0, str(REPO / "scripts"))
try:
    from rocky_say import synthesize as _tts_synthesize, server_start as _tts_server_start
except Exception:
    _tts_synthesize = None
    _tts_server_start = None


class ChatMessage(BaseModel):
    role: str
    content: str


class TTSRequest(BaseModel):
    text: str
    model: str = "yourtts"
    speed: float = 1.5
    transform: bool = True


class ChatRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    user_name: str | None = None
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    stream: bool = False


def build_app(model_path: str, model_id: str) -> FastAPI:
    tok = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/images", StaticFiles(directory=str(REPO / "images")), name="images")

    @app.get("/")
    def root():
        return FileResponse(UI_INDEX)

    @app.get("/v1/models")
    def list_models() -> dict[str, Any]:
        return {
            "object": "list",
            "data": [{"id": model_id, "object": "model", "owned_by": "local"}],
        }

    @app.post("/v1/tts")
    def tts(req: TTSRequest):
        if _tts_synthesize is None:
            raise HTTPException(503, "tts module unavailable")
        wav = _tts_synthesize(req.text, model=req.model, speed=req.speed, transform=req.transform)
        if not wav:
            raise HTTPException(503, "tts synthesis failed (check ~/.rocky_say setup)")
        return Response(content=wav, media_type="audio/wav")

    def _generate_kwargs(req: ChatRequest, input_ids: torch.Tensor) -> dict[str, Any]:
        return {
            "input_ids": input_ids,
            "max_new_tokens": req.max_tokens,
            "do_sample": req.temperature > 0,
            "temperature": max(req.temperature, 1e-5),
            "top_p": req.top_p,
            "pad_token_id": tok.pad_token_id or tok.eos_token_id,
        }

    def _prep_inputs(req: ChatRequest) -> torch.Tensor:
        msgs = [m.model_dump() for m in req.messages]
        name = _sanitize_name(req.user_name)
        prompt = _load_system_prompt(name)
        if prompt and not any(m["role"] == "system" for m in msgs):
            msgs = [{"role": "system", "content": prompt}] + msgs
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        return tok(text, return_tensors="pt").input_ids.to(model.device)

    @app.post("/v1/chat/completions")
    def chat(req: ChatRequest):
        input_ids = _prep_inputs(req)
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        created = int(time.time())

        if not req.stream:
            with torch.no_grad():
                out = model.generate(**_generate_kwargs(req, input_ids))
            text = tok.decode(out[0][input_ids.shape[-1]:], skip_special_tokens=True)
            return {
                "id": completion_id,
                "object": "chat.completion",
                "created": created,
                "model": model_id,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }],
            }

        streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)
        gen_kwargs = _generate_kwargs(req, input_ids) | {"streamer": streamer}
        Thread(target=model.generate, kwargs=gen_kwargs, daemon=True).start()

        def event_stream():
            for chunk in streamer:
                payload = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_id,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                yield f"data: {json.dumps(payload)}\n\n"
            done = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_id,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(done)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return app


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model-path", default="./models/grug-3b/model")
    p.add_argument("--model-id", default="grug-3b")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=67)
    p.add_argument("--no-tts", action="store_true", help="Skip auto-starting the TTS server")
    args = p.parse_args()

    if _tts_server_start and not args.no_tts:
        try:
            Thread(target=_tts_server_start, daemon=True).start()
        except Exception as e:
            print(f"tts server launch skipped: {e}", file=sys.stderr)

    uvicorn.run(build_app(args.model_path, args.model_id), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
