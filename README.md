# Rocky New to Ball 

## Self-host your own semi-superintelligent Rocky (Project Hail Mary) 

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
start it on desktop and try and fit it on a Raspberry Pi.

### Rules
- Self hosted
- True to character

### Roadmap
- Make it work (serve it)
  - *and hope ([we will check](https://github.com/AlexsJones/llmfit)) its not too much while my PC is runing an embedding models running for next 30 hours*
- A system prompt with some general guidance on who it is 
  - This could work well by splitting the text for all of Rocky's parts and
    dropping it into an LLM to write some behaviour based on what is in the script
- add TTS
- and then **maybe** finetune it to be really rocky-like (*but this could be overkill, it already seems to sound pretty good*)
  - it is a small model so there is potentially enough content in it to tune
  - If there isn't we'll use [doubleword](https://doubleword.ai/) batch to
    generate some more synthetic training examples based on the script,
    and roll with those

### Data 
*(deciding how I use it later but grabbed on first sesh)*
- PDF script
  - *pls don't sue, rocky is new to ball*
- Text from the script it using [https://www.pdfforge.org/online/en/extract-text](https://www.pdfforge.org/online/en/extract-text)
 because it doesn't need OCR and I'm not faffing with choosing a cli tool just to
feel high tech
  - As its a script, it is pretty nicely laid out (analysis below)

Whats in the script?
