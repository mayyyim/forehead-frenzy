#!/usr/bin/env python3
"""Emit artifact.html from index.html.

index.html is a complete standalone document because GitHub Pages serves it raw.
The claude.ai artifact runtime supplies its own <!doctype>/<head>/<body> skeleton and
rejects a page that brings its own, so the artifact copy is the same file with the
shell peeled off. One source, two hosts, no hand-editing.
"""
import io, re, sys

src = io.open("index.html", encoding="utf-8").read()

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
