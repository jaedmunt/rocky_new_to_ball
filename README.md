
<div align="center">

# Rocky New to Ball

## Self-host your own Rocky (Project Hail Mary) 

![fist my bump](/images/fistmybump.gif)

self-hosted Rocky (Project Hail Mary) - small local model, minimal web UI, optional voice (eerily similar)

Fun fact discovered while building this -the phrase ['Rocky new to ball'](https://www.youtube.com/watch?v=17OYHirpmqg) (receipts here) does not actually appear in the script. I added it back :)

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)
![Transformers](https://img.shields.io/badge/%F0%9F%A4%97%20Transformers-FFD21E?logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![uv](https://img.shields.io/badge/uv-DE5FE9?logo=astral&logoColor=white)
![Task](https://img.shields.io/badge/Task-29BEB0?logo=task&logoColor=white)

Powered by [grug-3b](https://huggingface.co/ProCreations/grug-3b), a LoRA of [Nanbeige4.2-3B](https://huggingface.co/Nanbeige/Nanbeige4.2-3B).

</div>

## Quick Start

```bash
task start   # start server in background
task open    # open the UI in your browser
task stop    # kill it
```

UI at <http://127.0.0.1:67>. See `Taskfile.yml` for the rest (`serve`, `restart`, `status`).

![demo](/images/demo-banner.png)


*Using the README a bit like a blog/journal but I hope you can find your way around
the project alright and enjoy it!*

Before the what, I offer four things led to this repo explaining why:
- I watched Project Hail Mary (great film btw)
- The README of the first repo on my Huggingface feed today 
  [grug-3b](https://huggingface.co/ProCreations/grug-3b) had a little something 
  to it, resembling the primitive way that rocky 'speaks' via his text to speech
  while having some pretty solid benchmarks for a model its size. 
  Excerpt:
 ```text
  - grug hard/easy think ratio 57x (median). base only 6x - base already near
    ceiling on easy question, cannot stretch. 
    grug start from almost nothing and stretch when problem earn it.
 ```
- Searching for the voice actor for Rocky, I came across this 
  gist [pedramamini/rocky_say](https://gist.github.com/pedramamini/fa5f6ef99dae79add220188419230642)
  building TTS for Rocky (kudos)
- I found the whole movie script in 20 seconds from [sciptslug](http://scriptslug.com/script/project-hail-mary-2026)
- the [pdf containing the text for each character](https://assets.scriptslug.com/live/pdf/scripts/project-hail-mary-2026.pdf.pdf)

...and I knew what had to be done. There's an audience at home for this so we'll
start it on desktop and try and ~~fit it on a Raspberry Pi~~.

### Rules
- Self hosted
- True to character

### Requirements
- Nvidia GPU w/ CUDA enabled (RTX 3060 12GB used for this; bf16 model ~6GB)
- [uv](https://docs.astral.sh/uv/) for python envs
- [go-task](https://taskfile.dev) for the `task ...` commands
- Python 3.11 (installed via uv)
- Optional (for voice): ~4 GB free disk for `coqui-tts` in a second venv

### Roadmap
- ✅ Make it work (serve it). transformers + FastAPI (sglang couldn't handle the Nanbeige arch)
- ✅ A system prompt with Rocky's speech patterns. See `data/processed/system_prompt.md`
- ✅ Minimal web UI at :67 with the rocky_dance gif that plays only while streaming
- ✅ TTS. YourTTS voice clone via a persistent worker on :59720
- **maybe** finetune it to be really rocky-like (*but this could be
  overkill, it already seems to write pretty well*)
  - it is a small model so there is potentially enough content in it to tune
  - If there isn't we'll use [doubleword](https://doubleword.ai/) batch to
    generate some more synthetic training examples based on the script,
    and roll with those
- Maybe serve [SillyTavern](https://docs.sillytavern.app/extensions/expression-images/) or somethhing else for sprites...
  - Rocky's block shape would be a good sprite

### Data 
*(deciding how I use it later but grabbed on first sesh)*

grug-3b has a 256k context window and we only feed 22 example lines in the prompt right now. The extract has 267 lines of Rocky dialogue in `data/processed/rocky_lines.txt` so plenty of room to shove more in.

I hand-added the baseball / new-to-human-things attitude into `data/processed/system_prompt.md` so Rocky still leans into the attitude he has in the film. 
- PDF script
  - *pls don't sue, rocky is new to ball*
- Text from the script it using [https://www.pdfforge.org/online/en/extract-text](https://www.pdfforge.org/online/en/extract-text)
 because it doesn't need OCR and I'm not faffing with choosing a cli tool just to
feel high tech
  - As its a script, it is pretty nicely laid out (analysis below)

### Whats in the script?

`Rocky` is mostly mentioned for what he does

![Rocky Action](/images/rocky_action.png)   

and what `ROCKY` says... 

![ROCKY SPEAKS](/images/rocky_speaks.png)

So this makes it not too hard to identify between action/mention and when he 
speaks. 

We mostly care about the speech so we get a rough estimate (because of multiline 
speech) w/:

```bash
rg ROCKY project-hail-mary-2026.txt | wc -l

# 196 
```

Interestingly, on first glance, 'Rocky new to ball', our favourite phrase, is
not mentioned once in the script. I first checked using 'new' and 'ball' in my
browser, and then in the text file to be sure. Huh. 

```bash
rg -i ball project-hail-mary-2026.txt

#605:container. Inside is a clear plastic ball. It appears empty
#608:But Grace is in his element. He takes the ball over to the
#2417:going to baseball games, eating ice *
#2896:Grace curls up into a ball and closes his eyes.
#3091:the sphere rolls forward... an extraterrestrial hamster ball.
#3322:Ceti E model back and forth in his hands like a tennis ball.
#3556:Grace and Rocky are now standing in the center of a baseball *
#3717:a weird metal balloon.
#4254:sampler like a ball and chain. He clips the free end of the
#4398:Smashes into his walls like a pinball -- he’s not restrained,
```

```bash
rg -i new project-hail-mary-2026.txt

#57:they’re pixels... we’re looking at a NEWSCAST.
#65:Every single person in the bar is glued to the NASA newsfeed.
#88:If I knew what was in the Petrova
#109:hear what the newsfeed is saying. Shh.
#439:through space. Heading towards that bright new star in the
#1235:Which is why you are now my new
#1312:Stratt conducts a meeting of the Hail Mary Team in the newly
#1786:Grace opens the new canister. It’s another model. It takes
#2201:He holds the new clock up, pleased with his work. *
#2596:thousand Newtons of force... *
#3053:You leave tunnel. I make new wall.
#3087:OUTSIDE: the new tunnel locks into place. Grace cycles the
#3226:I have a new roommate now.
#3277:Rocky sleeps in his newly built habitat.
#3281:It’s a new day. The lab is now transformed. Rocky’s
#3525:Rocky makes a new WHALE SOUND. Grace nods, types “Beach” *
#3601:New York City stretches out in all its glory. *
#3669:Need new name for planet...
#3702:You want to give the planet a new
#3705:Yes I give new name.
#4239:ON THE SCREENS behind Rocky -- NEW ALERTS start flashing...
#4525:and train a new science expert.
#4621:The room is a mess. Rocky has clearly been busy -- new tubes
#4807:Grace enters the dormitory and discovers Rocky wearing a NEW
#5159:He turns off the heating breakers. NEW ALARMS start to
#5204:Good news is, I tested it with
#5315:He inputs a new destination.
#5409:FROM BLACK... we find A NEW PLANET. One we’ve never seen *
#5420:room. Grace smiles. It’s a new day.
#5475:I have news, friend Grace.
```

### Serving Grug

I have other models running on my device (i5-100 and RTX 3060).

We shouldn't need much to serve this model and I'll add a hardware example when we're done. 

~~We'll use [LLMFit](https://github.com/AlexsJones/llmfit) to check the model on this device.~~

# :( 
![Open ze ticket, now](/images/llmfit_open_ticket.png)

Moving on...

We'll keep the model in the repo rather than globally and serve it in an env.

Default port is ~~30000~~ 67.

First tried sglang. grug-3b is a Nanbeige arch (`NanbeigeForCausalLM` and ships
its own `modeling_nanbeige.py` which needs `trust_remote_code=True`) and sglang's
model registry doesn't know about it. Same story for vLLM. Rather than write
a backend adapter for a 3B model, we serve it with plain transformers behind
a tiny FastAPI shim that speaks the OpenAI Chat Completions subset the web UI
needs. See [`scripts/serve.py`](scripts/serve.py).

Deps are in [`requirements.txt`](requirements.txt) and everything wires through
[`Taskfile.yml`](Taskfile.yml):

```bash
task setup   # one-time: pull ~8GB of grug-3b weights into ./models/
task start   # background: launches serve.py via uv
task open    # open http://127.0.0.1:67
task stop
```

The UI ([`ui/index.html`](ui/index.html)) is a single file. Dark monospace, one
input, the `rocky_dance.gif` frozen when idle and playing while streaming, a
collapsible `<think>` block, and an optional voice toggle. Or hit the API:

```bash
curl http://127.0.0.1:67/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"grug-3b","messages":[{"role":"user","content":"hi"}],"max_tokens":128}'
```

### Voice

The `/v1/tts` endpoint uses [pedramamini/rocky_say](https://gist.github.com/pedramamini/fa5f6ef99dae79add220188419230642)
(vendored in [`scripts/rocky_say.py`](scripts/rocky_say.py)) with YourTTS
zero-shot voice cloning. `serve.py` auto-launches a persistent TTS worker on
`:59720` at boot so subsequent calls are ~1-2 s instead of a 10 s subprocess
spawn. To enable it, one-time:

Pick a directory on a disk with ~4 GB free (mine lives outside the repo since
model weights are big). Then:

```bash
# create a second venv (coqui-tts pins transformers ~4.55, incompatible with grug)
uv venv "$ROCKY_DIR/venv" --python 3.11
uv pip install --python "$ROCKY_DIR/venv" --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cu124 \
    coqui-tts torch==2.5.1+cu124 torchaudio==2.5.1+cu124 transformers==4.55.0

# reference audio (~22 MB), used as the voice clone target
curl -L -o "$ROCKY_DIR/rocky_training_audio_scrubbed.wav" \
    https://pedramamini.com/dropbox/rocky_training_audio_scrubbed.wav
```

Then export `ROCKY_DIR` (e.g. `export ROCKY_DIR=~/.rocky_say` on unix, or
`$env:ROCKY_DIR = "$HOME/.rocky_say"` in PowerShell) before `task start` so
`serve.py` picks it up.

Then `task start`. First `/v1/tts` call pulls the YourTTS weights (~425 MB)
into HF cache; after that the worker stays warm.


