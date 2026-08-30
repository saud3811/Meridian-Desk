#!/usr/bin/env python3
"""Fetch all sources concurrently and emit a normalized JSON payload."""
import json, re, sys, time, html, hashlib
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

import feedparser
from sources import SOURCES, CAPS, classify_watch, classify_origin, pk_relevant

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
MAX_PER_FEED = 14
MAX_AGE_HOURS = 60

TAG_RE = re.compile(r"<[^>]+>")
# Clickbait/scraper noise that leaks into open web search feeds.
JUNK = re.compile(r"(viral video|original clip|full video|leaked (video|clip)|watch video|xxx|mms\b|link download|telegram link)", re.I)


def clean(text, limit=260):
    if not text:
        return ""
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit].rstrip() + ("…" if len(text) > limit else "")


def entry_time(e):
    for key in ("published_parsed", "updated_parsed"):
        val = e.get(key)
        if val:
            try:
                return datetime.fromtimestamp(time.mktime(val), tz=timezone.utc)
            except Exception:
                pass
    return None


def strip_source_suffix(title, source_name):
    # Google News appends " - Publisher"
    return re.sub(r"\s+-\s+[^-]{2,40}$", "", title).strip() or title


def pull(spec):
    name, code, url, desk, topic = spec
    out = []
    entries = []
    for attempt in range(3):
        try:
            feed = feedparser.parse(url, agent=UA)
            entries = feed.entries[:MAX_PER_FEED]
            if entries:
                break
        except Exception:
            pass
        time.sleep(1.5 * (attempt + 1))
    if not entries:
        return out
    now = datetime.now(timezone.utc)
    max_age = 168 if "when:7d" in url else MAX_AGE_HOURS
    cap = CAPS.get(name)
    if cap:
        entries = entries[:cap]
    for e in entries:
        title = clean(e.get("title", ""), 220)
        link = e.get("link", "")
        if not title or not link or JUNK.search(title):
            continue
        if not pk_relevant(title, url, desk):
            continue
        ts = entry_time(e)
        if ts and (now - ts).total_seconds() > max_age * 3600:
            continue
        is_gnews = "news.google.com" in url
        publisher = ""
        if is_gnews:
            title = strip_source_suffix(title, name)
            src = e.get("source") or {}
            publisher = clean(src.get("title", ""), 60)
        summary = clean(e.get("summary", "") or e.get("description", ""))
        if is_gnews:
            summary = ""
        out.append({
            "t": title,
            "u": link,
            "s": name,
            "c": code,
            "d": desk,
            "k": topic,
            "_ts": ts,
            "x": summary,
            "p": publisher,
            "w": classify_watch(title),
            "o": classify_origin(name, publisher),
        })

    # Some publishers stamp ahead of UTC. Shift the whole feed back by its own
    # skew so entries keep their true relative order instead of pinning to "now".
    stamped = [i for i in out if i["_ts"]]
    if stamped:
        skew = max(i["_ts"] for i in stamped) - now
        if skew.total_seconds() > 60:
            for i in stamped:
                i["_ts"] = i["_ts"] - skew
    for i in out:
        i["ts"] = i["_ts"].isoformat().replace("+00:00", "Z") if i["_ts"] else None
        del i["_ts"]
    return out


BIZ = re.compile(r"\b(econom|market|stock|share price|inflation|imf|rupee|dollar|tariff|trade deal|gdp|budget|tax|revenue|earnings|profit|bank|investor|bourse|psx|kse-100|oil price|opec|interest rate|central bank|fiscal|debt|exports?|imports?|currency|nasdaq|s&p|dow jones|bitcoin|crypto)\b", re.I)
TECH = re.compile(r"\b(artificial intelligence|\bai\b|chatgpt|openai|anthropic|google deepmind|machine learning|software|smartphone|semiconductor|chipmaker|startup|app\b|cyber|hacking|data breach|satellite|spacex|robot|quantum|algorithm|iphone|android|nvidia|tesla|meta platforms|tiktok|social media)\b", re.I)
POL = re.compile(r"\b(elections?|parliament|senate|assembly|ministers?|president|prime minister|courts?|verdict|protests?|strikes?|military|troops|airstrikes?|killed|arrests?|police|treaty|summit|sanctions?|refugees?|border|wars?|ceasefire|diplomat\w*|militants?|casualt\w+)\b", re.I)


def reclassify(it):
    """Feed-assigned beat is the default; a confident keyword hit overrides it."""
    blob = it["t"] + " " + it["x"]
    if TECH.search(blob):
        it["k"] = "tech"
    elif BIZ.search(blob):
        it["k"] = "business"
    elif POL.search(blob):
        it["k"] = "politics"
    return it


def diversify(items, run=2):
    """Keep reverse-chronological order but stop one feed owning a whole block."""
    out, held = [], []
    for it in items:
        tail = [x["s"] for x in out[-run:]]
        if len(tail) == run and all(t == it["s"] for t in tail):
            held.append(it)
            continue
        out.append(it)
        for i, h in enumerate(held):
            if not (out and out[-1]["s"] == h["s"]):
                out.append(held.pop(i))
                break
    return out + held


def main():
    with ThreadPoolExecutor(max_workers=16) as ex:
        results = list(ex.map(pull, SOURCES))

    items, seen_url, seen_title = [], set(), set()
    for chunk in results:
        for it in chunk:
            ukey = it["u"].split("?")[0]
            tkey = re.sub(r"[^a-z0-9]", "", it["t"].lower())[:70]
            if ukey in seen_url or (tkey and tkey in seen_title):
                continue
            seen_url.add(ukey)
            seen_title.add(tkey)
            items.append(it)

    items = [reclassify(i) for i in items]
    items.sort(key=lambda i: i["ts"] or "", reverse=True)
    items = diversify([i for i in items if i["d"] == "WORLD"]) + \
            diversify([i for i in items if i["d"] == "PAKISTAN"])

    live = sorted({i["s"] for i in items})
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "counts": {
            "total": len(items),
            "world": sum(1 for i in items if i["d"] == "WORLD"),
            "pakistan": sum(1 for i in items if i["d"] == "PAKISTAN"),
            "sources": len(live),
            "watch24": sum(1 for i in items if i["w"] and i["ts"]
                           and (datetime.now(timezone.utc) -
                                datetime.fromisoformat(i["ts"].replace("Z", "+00:00"))).total_seconds() < 86400),
            "watch": sum(1 for i in items if i["w"]),
            "feeds_ok": sum(1 for r in results if r),
            "feeds_total": len(SOURCES),
        },
        "items": items,
    }
    out = sys.argv[1] if len(sys.argv) > 1 else "news_data.json"
    with open(out, "w") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps(payload["counts"], indent=2))
    dead = [SOURCES[i][0] for i, r in enumerate(results) if not r]
    if dead:
        print("EMPTY:", ", ".join(dead), file=sys.stderr)


if __name__ == "__main__":
    main()
