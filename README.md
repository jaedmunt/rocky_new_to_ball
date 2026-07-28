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
- and then **maybe** finetune it to be really rocky-like (*but this could be 
  overkill, it already seems to write pretty well*)
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

# Serving Grug
