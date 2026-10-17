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

# ---------------------------------------------------------------- words.html
# A browsable reference for the whole vocabulary, generated from the same SOURCES
# the game plays from, so the two can never drift apart.

def deck_recipes(src_text):
    import json as _json, re as _re, subprocess as _sp, tempfile, os
    block = _re.search(r"var DECKS = \[.*?\n  \];", src_text, _re.S).group(0)
    fd, path = tempfile.mkstemp(suffix=".js")
    os.write(fd, (block + "\nconsole.log(JSON.stringify(DECKS));").encode())
    os.close(fd)
    out = _json.loads(_sp.check_output(["node", path]).decode())
    os.unlink(path)
    return out

def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

RECIPES = deck_recipes(src)
BY_ID = {d["id"]: d for d in DECKS_AUDIT}

total_words = []
for d in DECKS_AUDIT:
    total_words += d["words"]
uniq = []
seen_u = set()
for w in total_words:
    if w.lower() not in seen_u:
        seen_u.add(w.lower()); uniq.append(w)
one = len([w for w in uniq if " " not in w])
multi = len(uniq) - one

sections = []
for r in RECIPES:
    deck_seen = set()
    groups = []
    for sid in r["from"]:
        src_deck = BY_ID[sid]
        words = []
        for w in src_deck["words"]:
            if w.lower() in deck_seen:
                continue
            deck_seen.add(w.lower()); words.append(w)
        words.sort(key=lambda x: x.lower())
        chips = "".join(
            '<li class="w%s" data-w="%s">%s</li>' % (
                " multi" if " " in w else "", esc(w.lower()), esc(w))
            for w in words)
        groups.append(
            '<div class="grp" data-count="%d"><h3>%s <span>%d</span></h3><ul>%s</ul></div>'
            % (len(words), esc(src_deck["name"]), len(words), chips))
    sections.append(
        '<section class="deck" id="d-%s"><header><h2>%s</h2><p>%d words</p></header>%s</section>'
        % (r["id"], esc(r["name"]), len(deck_seen), "".join(groups)))

nav = "".join('<a href="#d-%s">%s <b>%d</b></a>' % (r["id"], esc(r["name"]), len(BY_ID and set()) or 0)
              for r in RECIPES)
nav = "".join(
    '<a href="#d-%s">%s</a>' % (r["id"], esc(r["name"])) for r in RECIPES)

WORDS_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="dark">
<title>Forehead Frenzy Word List</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Chivo:wght@400;600;800&display=swap">
<style>
  [hidden]{display:none !important}
  :root{--ink:#190E33;--ink-2:#221340;--card:#2E1B57;--cream:#F8F1E3;--lav:#B0A0D4;--lav-dim:#7C6CA3;
        --amber:#FFC247;--display:"Anton","Arial Narrow",sans-serif;--body:"Chivo",Arial,sans-serif}
  *{box-sizing:border-box}
  body{margin:0;background:var(--ink);color:var(--cream);font-family:var(--body);
       -webkit-text-size-adjust:100%%}
  .wrap{max-width:860px;margin:0 auto;padding-block:26px 48px;padding-left:18px;padding-right:18px}
  .eyebrow{font-size:.66rem;letter-spacing:.3em;text-transform:uppercase;color:var(--lav);margin:0 0 8px}
  h1{font-family:var(--display);font-weight:400;text-transform:uppercase;font-size:clamp(2rem,9vw,3.2rem);
     line-height:.9;margin:0 0 14px}
  .stats{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 20px;padding:0;list-style:none}
  .stats li{background:var(--card);border-radius:10px;padding:9px 13px;font-size:.78rem;color:var(--lav)}
  .stats b{font-family:var(--display);font-size:1.05rem;color:var(--amber);margin-right:6px;
           font-variant-numeric:tabular-nums}
  .tools{position:sticky;top:0;z-index:5;background:var(--ink);padding:12px 0 14px;
         border-bottom:1px solid #30204F;margin-bottom:22px}
  #q{width:100%%;background:var(--ink-2);border:2px solid #3A2369;border-radius:12px;color:var(--cream);
     font-family:inherit;font-size:1rem;padding:13px 15px}
  #q:focus{outline:none;border-color:var(--amber)}
  .filters{display:flex;gap:7px;margin-top:10px;flex-wrap:wrap}
  .filters button{background:var(--card);border:2px solid transparent;border-radius:999px;color:var(--lav);
                  font-family:inherit;font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;
                  padding:7px 13px;cursor:pointer}
  .filters button[aria-pressed="true"]{border-color:var(--amber);color:var(--amber)}
  .hint{font-size:.74rem;color:var(--lav-dim);margin:9px 0 0}
  .jump{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 26px}
  .jump a{background:var(--ink-2);border:1px solid #352257;border-radius:999px;padding:6px 11px;
          font-size:.72rem;color:var(--lav);text-decoration:none}
  .deck{margin-bottom:34px;scroll-margin-top:110px}
  .deck > header{display:flex;align-items:baseline;justify-content:space-between;gap:12px;
                 border-bottom:2px solid var(--amber);padding-bottom:7px;margin-bottom:16px}
  .deck h2{font-family:var(--display);font-weight:400;text-transform:uppercase;font-size:1.45rem;margin:0}
  .deck > header p{margin:0;font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;color:var(--lav-dim);
                   font-variant-numeric:tabular-nums}
  .grp{margin-bottom:16px}
  .grp h3{font-size:.64rem;letter-spacing:.22em;text-transform:uppercase;color:var(--lav-dim);
          font-weight:600;margin:0 0 8px}
  .grp h3 span{color:#4E3C77;margin-left:5px;font-variant-numeric:tabular-nums}
  .grp ul{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
  .w{background:var(--card);border-radius:7px;padding:6px 10px;font-size:.86rem;line-height:1.2}
  .w.multi{background:transparent;border:1px dashed #4E3C77;color:var(--lav)}
  mark{background:var(--amber);color:#2A1700;border-radius:3px;padding:0 1px}
  .none{color:var(--lav-dim);font-size:.9rem}
  footer{border-top:1px solid #30204F;margin-top:30px;padding-top:16px;font-size:.76rem;color:var(--lav-dim);
         line-height:1.6}
  footer a{color:var(--amber)}
</style>
</head>
<body>
<div class="wrap">
  <p class="eyebrow">Forehead Frenzy</p>
  <h1>Every word in the game</h1>
  <ul class="stats">
    <li><b>%(uniq)d</b>unique words</li>
    <li><b>%(one)d</b>single words</li>
    <li><b>%(multi)d</b>multi-word names</li>
    <li><b>%(decks)d</b>playable decks</li>
  </ul>

  <div class="tools">
    <input id="q" type="search" placeholder="Search for a word…" autocomplete="off" spellcheck="false">
    <div class="filters">
      <button id="f-all" aria-pressed="true">Everything</button>
      <button id="f-one" aria-pressed="false">Single words</button>
      <button id="f-multi" aria-pressed="false">Multi-word only</button>
    </div>
    <p class="hint" id="count"></p>
  </div>

  <nav class="jump">%(nav)s</nav>

  %(sections)s

  <footer>
    Dashed entries are the multi-word ones &mdash; famous names, titles, and compounds that work as
    one word. Everything else is a single word.<br>
    A word can sit in two decks (a wheelchair is both a body thing and a way of getting around),
    so the entry count below the search box runs slightly above the unique-word total.<br>
    Generated from the game's own word lists by <code>build.py</code>, so this page cannot drift
    out of date. <a href="./">Back to the game</a>.
  </footer>
</div>

<script>
(function(){
  var q = document.getElementById("q"), count = document.getElementById("count");
  var words = [].slice.call(document.querySelectorAll(".w"));
  var groups = [].slice.call(document.querySelectorAll(".grp"));
  var decks = [].slice.call(document.querySelectorAll(".deck"));
  var btns = {all:document.getElementById("f-all"), one:document.getElementById("f-one"),
              multi:document.getElementById("f-multi")};
  var mode = "all";

  function apply(){
    var term = q.value.trim().toLowerCase();
    var shown = 0;
    words.forEach(function(el){
      var w = el.dataset.w;
      var isMulti = el.classList.contains("multi");
      var ok = (mode === "all") || (mode === "one" && !isMulti) || (mode === "multi" && isMulti);
      if(ok && term) ok = w.indexOf(term) !== -1;
      el.hidden = !ok;
      if(ok){
        shown++;
        if(term){
          var raw = el.textContent, i = raw.toLowerCase().indexOf(term);
          el.innerHTML = i < 0 ? raw
            : raw.slice(0,i) + "<mark>" + raw.slice(i, i+term.length) + "</mark>" + raw.slice(i+term.length);
        } else if(el.innerHTML.indexOf("<mark") !== -1){
          el.innerHTML = el.textContent;
        }
      }
    });
    groups.forEach(function(g){
      g.hidden = !g.querySelector(".w:not([hidden])");
    });
    decks.forEach(function(d){
      d.hidden = !d.querySelector(".w:not([hidden])");
    });
    count.textContent = shown === words.length
      ? "Showing all " + shown + " entries"
      : "Showing " + shown + " of " + words.length + " entries";
  }
  function setMode(m){
    mode = m;
    Object.keys(btns).forEach(function(k){ btns[k].setAttribute("aria-pressed", String(k === m)); });
    apply();
  }
  q.addEventListener("input", apply);
  btns.all.addEventListener("click", function(){ setMode("all"); });
  btns.one.addEventListener("click", function(){ setMode("one"); });
  btns.multi.addEventListener("click", function(){ setMode("multi"); });
  apply();
})();
</script>
</body>
</html>
""" % {"uniq": len(uniq), "one": one, "multi": multi, "decks": len(RECIPES),
       "nav": nav, "sections": "\n  ".join(sections)}

io.open("words.html", "w", encoding="utf-8").write(WORDS_HTML)
print("words.html written (%d entries, %d decks)" % (len(uniq), len(RECIPES)))
