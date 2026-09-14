#!/usr/bin/env python3
"""Fetch all sources concurrently and emit a normalized JSON payload."""
import json, os, re, sys, time, html, hashlib
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

import feedparser
from sources import (SOURCES, CAPS, GDELT_QUERIES, classify_watch, classify_origin,
                     pk_relevant, region_of, is_pk_relevant)
import gdelt

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
            "lang": "English",
            "cty": "",
            "img": "",
            "g": 0,
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


def collect_gdelt(cache_dir="data"):
    """Run the GDELT query set. Returns (items, volume_series, status_by_key).

    Never raises: a throttled or broken query falls back to its cache, and a
    missing cache yields nothing rather than failing the build.
    """
    items, volume, status = [], [], {}
    for i, (key, label, code, q, mode, timespan, desk, topic) in enumerate(GDELT_QUERIES):
        if i:
            time.sleep(gdelt.GAP)
        payload, st = gdelt.query(q, key, mode=mode, timespan=timespan,
                                  cache_dir=cache_dir)
        status[key] = st
        if mode == "timelinevol":
            volume = gdelt.timeline_series(payload)
            continue
        rows = gdelt.to_items(payload, label, code, desk, topic)
        kept = []
        for r in rows:
            r["w"] = classify_watch(r["t"])
            r["o"] = region_of(r["cty"], r["lang"])
            # A Pakistan-desk item must actually be about Pakistan. GDELT's
            # language filters return plenty of regional news that merely
            # shares a query, and it has no business on this desk.
            if desk == "PAKISTAN" and not (r["w"] or is_pk_relevant(r["t"])):
                continue
            kept.append(r)
        if len(kept) < len(rows):
            print(f"    dropped {len(rows)-len(kept)} off-topic items from {key}")
        items.extend(kept)
    return items, volume, status


def main():
    print("GDELT (primary):")
    g_items, g_volume, g_status = collect_gdelt()
    print(f"  -> {len(g_items)} items, {sum(1 for i in g_items if i['w'])} naming a principal")

    print("RSS (backup):")
    with ThreadPoolExecutor(max_workers=16) as ex:
        results = list(ex.map(pull, SOURCES))

    items, seen_url, seen_title = [], set(), set()
    for chunk in [g_items] + results:
        for it in chunk:
            ukey = it["u"].split("?")[0]
            tkey = re.sub(r"[^a-z0-9]", "", it["t"].lower())[:70]
            if ukey in seen_url or (tkey and tkey in seen_title):
                continue
            seen_url.add(ukey)
            seen_title.add(tkey)
            items.append(it)

    # Rolling store. GDELT is intermittently empty and publishers rate-limit,
    # so each run merges into the previous run's items rather than replacing
    # them. Anything older than the window is pruned below.
    out_path = sys.argv[1] if len(sys.argv) > 1 else "news_data.json"
    carried = 0
    if os.path.exists(out_path):
        try:
            prev = json.load(open(out_path, encoding="utf-8"))
            for it in prev.get("items", []):
                uk = it["u"].split("?")[0]
                tk = re.sub(r"[^a-z0-9]", "", it["t"].lower())[:70]
                if uk in seen_url or (tk and tk in seen_title):
                    continue
                # Re-apply current rules to carried items, so tightening a
                # filter cleans out history instead of only affecting new pulls.
                if (it.get("d") == "PAKISTAN" and not it.get("w")
                        and not is_pk_relevant(it["t"])):
                    continue
                seen_url.add(uk); seen_title.add(tk)
                items.append(it); carried += 1
        except Exception as e:
            print(f"  (no usable previous store: {e})")
    print(f"carried forward {carried} items from the previous run")

    # Prune: 60h for the desks, 7 days for watch items (they are sparse).
    now_utc = datetime.now(timezone.utc)
    def _age_h(it):
        if not it.get("ts"):
            return 1e9
        try:
            return (now_utc - datetime.fromisoformat(it["ts"].replace("Z", "+00:00"))).total_seconds() / 3600
        except Exception:
            return 1e9
    items = [i for i in items if _age_h(i) <= (168 if i.get("w") else 60)]

    items = [reclassify(i) for i in items]
    items.sort(key=lambda i: i["ts"] or "", reverse=True)
    items = diversify([i for i in items if i["d"] == "WORLD"]) + \
            diversify([i for i in items if i["d"] == "PAKISTAN"])

    live = sorted({i["s"] for i in items})
    g_n = sum(1 for i in items if i.get("g"))
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
            "gdelt": g_n,
            "mena": sum(1 for i in items if i.get("o") == "MENA"),
            "urdu": sum(1 for i in items if i.get("lang") == "Urdu"),
            "arabic": sum(1 for i in items if i.get("lang") == "Arabic"),
        },
        "gdelt_status": g_status,
        "volume": g_volume,
        "attribution": gdelt.ATTRIBUTION,
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
