#!/usr/bin/env python3
"""
GDELT DOC 2.0 client.

Data courtesy of The GDELT Project (https://www.gdeltproject.org/), free for
any use with attribution.

Two things matter here and both are lessons from production:

1. GDELT rate-limits hard and publishes no numbers. Every call retries with
   exponential backoff, and every successful result is cached to disk. If a run
   is throttled, the cached result is served instead — stale, clearly marked,
   but never empty. The Zardari watch going blank once was enough.

2. GDELT matches queries against machine-translated text but returns the
   ORIGINAL headline. An English query for "Bilawal Bhutto" therefore returns
   Urdu and Arabic articles with Urdu and Arabic titles. That is the whole
   reason this works — and the reason name matching must handle those scripts.
"""
import json, os, re, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone

BASE = "https://api.gdeltproject.org/api/v2/doc/doc"
UA = ("Mozilla/5.0 (compatible; MeridianDesk/1.0; "
      "+https://github.com/saud3811/Meridian-Desk)")
ATTRIBUTION = "Data courtesy of The GDELT Project — https://www.gdeltproject.org/"

TIMEOUT = 90
MAX_TRIES = 5
BASE_WAIT = 20
GAP = 6          # polite pause between successive queries


def _cache_path(cache_dir, key):
    safe = re.sub(r"[^a-z0-9]+", "_", key.lower())[:80]
    return os.path.join(cache_dir, f"gdelt_{safe}.json")


def query(q, key, mode="artlist", timespan="24h", maxrecords=250,
          cache_dir="data", sort="datedesc"):
    """Run one DOC query. Returns (payload, status) where status is
    'live', 'cached' or 'empty'."""
    params = {"query": q, "mode": mode, "format": "json", "timespan": timespan}
    if mode == "artlist":
        params["maxrecords"] = maxrecords
        params["sort"] = sort
    url = BASE + "?" + urllib.parse.urlencode(params)
    os.makedirs(cache_dir, exist_ok=True)
    cache = _cache_path(cache_dir, key)

    wait = BASE_WAIT
    for attempt in range(MAX_TRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            raw = urllib.request.urlopen(req, timeout=TIMEOUT).read()
            text = raw.decode("utf-8", "replace").strip()
            if not text.startswith("{"):
                # GDELT reports query syntax errors as plain text, not JSON.
                print(f"  gdelt[{key}] rejected the query: {text[:110]}")
                break
            payload = json.loads(text)
            n = len(payload.get("articles", payload.get("timeline", [])))

            # GDELT soft-throttles by returning HTTP 200 with an EMPTY list
            # rather than a 429. Observed directly: a query returning 53
            # articles returned 0 an hour later, then worked again. So an
            # empty live result is treated as a throttle, never as truth, and
            # must never overwrite a good cache. This is the exact failure
            # that silently emptied the watch once already.
            if n == 0 and os.path.exists(cache):
                try:
                    prev = json.load(open(cache, encoding="utf-8"))
                    if len(prev.get("articles", prev.get("timeline", []))) > 0:
                        print(f"  gdelt[{key}] live result was empty — keeping "
                              f"cache from {prev.get('_fetched')}")
                        return prev, "cached"
                except Exception:
                    pass

            payload["_fetched"] = datetime.now(timezone.utc).isoformat(
                timespec="seconds").replace("+00:00", "Z")
            payload["_query"] = q
            if n > 0:
                with open(cache, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
            print(f"  gdelt[{key}] {n} records (live)")
            return payload, "live" if n else "empty"
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(wait)
                wait = int(wait * 1.6)
                continue
            print(f"  gdelt[{key}] HTTP {e.code}")
            break
        except Exception as e:
            print(f"  gdelt[{key}] {type(e).__name__}: {e}")
            break

    if os.path.exists(cache):
        try:
            payload = json.load(open(cache, encoding="utf-8"))
            print(f"  gdelt[{key}] throttled — using cache from {payload.get('_fetched')}")
            return payload, "cached"
        except Exception:
            pass
    print(f"  gdelt[{key}] no data and no cache")
    return {"articles": []}, "empty"


# ---------------------------------------------------------------------------
# Normalisation into the same item shape the RSS pipeline produces
# ---------------------------------------------------------------------------
_SEEN = re.compile(r"^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$")

# A handful of GDELT-indexed domains are content farms and scrapers.
JUNK_DOMAINS = {
    "newsmakers.pk", "prokerala.com", "thailandnews.net", "menafn.com",
    "bignewsnetwork.com", "webindia123.com", "newkerala.com", "devdiscourse.com",
    "riotimesonline.com", "theglobalherald.com", "worldakkam.com", "newsbeezer.com",
    "pledgetimes.com", "archyde.com", "explica.co", "nationworldnews.com",
    "californianewstimes.com", "sunnewsonline.com", "zoomtventertainment.com",
}


def parse_seendate(s):
    m = _SEEN.match((s or "").strip())
    if not m:
        return None
    y, mo, d, h, mi, se = (int(x) for x in m.groups())
    try:
        return datetime(y, mo, d, h, mi, se, tzinfo=timezone.utc)
    except ValueError:
        return None


def to_items(payload, feed_name, code, desk, topic, junk_domains=JUNK_DOMAINS):
    """Turn a DOC artlist payload into pipeline items."""
    out = []
    now = datetime.now(timezone.utc)
    for a in payload.get("articles", []):
        title = (a.get("title") or "").strip()
        url = (a.get("url") or "").strip()
        domain = (a.get("domain") or "").strip().lower()
        if not title or not url:
            continue
        if domain in junk_domains:
            continue
        ts = parse_seendate(a.get("seendate"))
        if ts and ts > now:
            ts = now
        out.append({
            "t": title,
            "u": url,
            "s": feed_name,
            "c": code,
            "d": desk,
            "k": topic,
            "ts": ts.isoformat().replace("+00:00", "Z") if ts else None,
            "x": "",
            "p": domain,
            "lang": a.get("language") or "",
            "cty": a.get("sourcecountry") or "",
            "img": a.get("socialimage") or "",
            "g": 1,                       # came from GDELT
        })
    return out


def timeline_series(payload):
    """Extract [(iso_datetime, value), ...] from a timelinevol payload."""
    series = []
    for block in payload.get("timeline", []):
        for pt in block.get("data", []):
            series.append((pt.get("date"), pt.get("value")))
        break
    return series
