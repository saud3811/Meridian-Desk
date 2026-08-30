#!/usr/bin/env python3
"""
Assemble the deployable page.

  src/template.html + data/news_data.json + data/summary.json  ->  dist/index.html

The template carries two marked blocks that this script swaps. Nothing else in
the template is touched, so the page's design and the data stay independent.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "src", "template.html")
DATA = os.path.join(ROOT, "data", "news_data.json")
BRIEF = os.path.join(ROOT, "data", "summary.json")
OUT = os.path.join(ROOT, "dist", "index.html")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Global and Pakistan news desk - world wires, a Pakistan desk of equal weight, and a Bhutto-Zardari watch. Rebuilt automatically.">
<meta name="color-scheme" content="dark light">
<meta property="og:title" content="Meridian News Desk">
<meta property="og:description" content="World wires and a Pakistan desk, side by side, refreshed automatically.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128225;</text></svg>">
<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>
</head>
<body>
"""
TAIL = "\n</body>\n</html>\n"


def swap(text, start, end, name, blob):
    out = re.sub(re.escape(start) + r".*?" + re.escape(end),
                 lambda _: f"{start}\nconst {name} = {blob};\n{end}",
                 text, flags=re.S)
    if start not in out:
        sys.exit(f"error: {name} markers not found in template")
    return out


def main():
    body = open(TPL, encoding="utf-8").read()

    if not os.path.exists(DATA):
        sys.exit(f"error: {DATA} missing - run src/fetch_news.py first")
    news = json.load(open(DATA, encoding="utf-8"))
    blob = json.dumps(news, ensure_ascii=False, separators=(",", ":")).replace("</script", "<\\/script")
    body = swap(body, "/*__NEWS_DATA_START__*/", "/*__NEWS_DATA_END__*/", "NEWS_DATA", blob)

    if os.path.exists(BRIEF):
        brief = json.dumps(json.load(open(BRIEF, encoding="utf-8")),
                           ensure_ascii=False, separators=(",", ":"))
        body = swap(body, "/*__SUMMARY_START__*/", "/*__SUMMARY_END__*/", "SUMMARY",
                    brief.replace("</script", "<\\/script"))
    else:
        print("note: no summary.json - the Summary panel will say none is available")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(HEAD + body + TAIL)

    c = news["counts"]
    print(f"built {OUT} ({os.path.getsize(OUT)/1024:.0f} KB) - "
          f"{c['total']} headlines, {c['feeds_ok']}/{c['feeds_total']} feeds")


if __name__ == "__main__":
    main()
