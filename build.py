#!/usr/bin/env python3
"""Emit artifact.html from index.html.

index.html is a complete standalone document because GitHub Pages serves it raw.
The claude.ai artifact runtime supplies its own <!doctype>/<head>/<body> skeleton and
rejects a page that brings its own, so the artifact copy is the same file with the
shell peeled off. One source, two hosts, no hand-editing.
"""
import io, re, sys

src = io.open("index.html", encoding="utf-8").read()

# A word on a forehead has to be readable at a glance, so entries are single words
# except in the decks that are proper nouns by nature, plus a short list of compounds
# that behave as one lexical item. Anything else is a phrase and gets flagged here.
PROPER = {"places", "screen", "toons", "people", "tales", "holidays"}
COMPOUND_OK = {
    "hot dog", "french fries", "ice cream", "bubble tea", "hot pot", "dim sum", "egg tart",
    "fried rice", "peanut butter", "chicken wing", "fried egg", "fish and chips", "cotton candy",
    "chewing gum", "hot chocolate", "birthday cake", "alarm clock", "frying pan", "cutting board",
    "vacuum cleaner", "trash can", "hair dryer", "washing machine", "remote control", "toilet paper",
    "air conditioner", "needle and thread", "piggy bank", "photo album", "t-shirt", "bow tie",
    "high heels", "face mask", "nail polish", "runny nose", "sore throat", "broken arm", "x-ray",
    "deep breath", "in love", "pencil case", "report card", "graduation cap", "test tube", "lab coat",
    "field trip", "sticky note", "business card", "name tag", "coffee break", "video call",
    "fire drill", "pop quiz", "polar bear", "outer space", "northern lights", "spider web",
    "bird nest", "autumn leaves", "cherry blossom", "full moon", "shooting star", "heat wave",
    "fire truck", "police car", "school bus", "garbage truck", "hot air balloon", "cruise ship",
    "jet ski", "cable car", "roller coaster", "traffic light", "gas station", "train station",
    "bus stop", "flat tire", "traffic jam", "rush hour", "parking lot", "ping pong", "ice skating",
    "hide and seek", "jump rope", "horse riding", "ice hockey", "high jump", "long jump", "shot put",
    "pole vault", "relay race", "water polo", "bungee jumping", "rock paper scissors", "hula hoop",
    "tug of war", "arm wrestling", "video games", "penalty kick", "slam dunk", "home run", "red card",
    "hat trick", "police officer", "taxi driver", "tour guide", "flight attendant", "bus driver",
    "construction worker", "security guard", "news anchor", "orchestra conductor", "electric guitar",
    "pipe organ", "bamboo flute", "bongo drum", "rock band", "pop song", "country music",
    "classical music", "k-pop", "hip hop", "national anthem", "sheet music", "air guitar",
    "guitar solo", "music video", "happy birthday song", "desktop computer", "fitness tracker",
    "vr headset", "game console", "game controller", "usb stick", "hard drive", "sim card", "qr code",
    "selfie stick", "security camera", "smart speaker", "e-reader", "group chat", "like button",
    "dark mode", "low battery", "loading screen", "pop-up ad", "airplane mode", "screen time",
    "app store", "software update", "computer virus", "ai chatbot", "face unlock", "double click",
    "screen share", "cloud storage", "best friend", "old man", "old lady", "in-laws", "family photo",
    "bedtime story", "pocket money", "only child", "family dinner", "first steps", "post office",
    "movie theater", "police station", "fire station", "public library", "shopping mall",
    "construction site", "apartment building", "zebra crossing", "street lamp", "vending machine",
    "public toilet", "fire hydrant", "manhole cover", "graffiti wall", "food truck", "night market",
    "car wash", "revolving door", "parking meter", "shopping cart", "credit card", "mobile payment",
    "price tag", "online shopping", "free shipping", "out of stock", "window shopping", "gift card",
    "shopping spree", "grocery list", "magic lamp", "magic carpet", "crystal ball", "magic wand",
    "flying broom", "glass slipper", "poisoned apple", "golden egg", "treasure chest", "pirate ship",
    "haunted castle", "wishing well", "talking mirror", "404 error",
    "watering can", "bad breath", "group project", "ice cream truck", "fitting room",
    "black friday", "flash sale", "bowling alley", "water ski", "hot spring", "ping pong",
}

def audit(src_text):
    import json as _json, re as _re, subprocess as _sp, tempfile, os
    block = _re.search(r"var SOURCES = \[.*?\n  \];", src_text, _re.S).group(0)
    fd, path = tempfile.mkstemp(suffix=".js")
    os.write(fd, (block + "\nconsole.log(JSON.stringify(SOURCES));").encode())
    os.close(fd)
    decks = _json.loads(_sp.check_output(["node", path]).decode())
    os.unlink(path)
    bad = []
    for d in decks:
        if d["id"] in PROPER:
            continue
        for w in d["words"]:
            if " " in w and w.lower() not in COMPOUND_OK:
                bad.append((d["id"], w))
    return decks, bad

DECKS_AUDIT, PHRASES = audit(src)
if PHRASES:
    print("phrases outside the allowlist (%d):" % len(PHRASES))
    for did, w in PHRASES:
        print("  %-10s %s" % (did, w))
    sys.exit("fix or allowlist the entries above")
print("word audit: %d decks, %d words, no stray phrases"
      % (len(DECKS_AUDIT), sum(len(d["words"]) for d in DECKS_AUDIT)))

body = re.search(r"<title>.*?</style>", src, re.S)
rest = re.search(r"<main>.*?</script>", src, re.S)
if not body or not rest:
    sys.exit("index.html no longer has the expected shape; fix build.py")

out = body.group(0) + "\n\n" + rest.group(0) + "\n"
for banned in ("<!doctype", "<html", "<head", "<body"):
    if banned in out.lower():
        sys.exit("artifact fragment still carries %s" % banned)
io.open("artifact.html", "w", encoding="utf-8").write(out)
print("artifact.html written (%d bytes)" % len(out))
