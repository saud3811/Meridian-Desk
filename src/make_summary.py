#!/usr/bin/env python3
"""
Produce summary.json — the Daily Brief the dashboard's Summary button shows.

Two modes, chosen automatically:

  AUTO (default, no API key, no cost)
      Clusters each section's headlines and ranks the clusters by how many
      distinct publishers carried them. Corroboration is the signal: a story
      eight outlets ran independently is the lead, and one outlet's exclusive
      is flagged as exactly that. Output is assembled, not written.

  WRITTEN (when ANTHROPIC_API_KEY is set)
      Sends the digest to Claude with editorial instructions and gets back
      composed prose. Falls back to AUTO on any failure, so the build never
      breaks because of an API problem.

  python3 make_summary.py news_data.json summary.json [hours]
"""
import json, os, re, sys
from collections import defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sources import classify_watch  # noqa: E402,F401  (kept for parity with the pipeline)

SECTIONS = [
    ("WORLD",    "World Desk",             None),
    ("PAKISTAN", "Pakistan Desk",          None),
    ("AAZ",      "Asif Ali Zardari",       "AAZ"),
    ("PRES",     "The Presidency",         "PRES"),
    ("BBZ",      "Bilawal Bhutto Zardari", "BBZ"),
    ("ABZ",      "Aseefa Bhutto Zardari",  "ABZ"),
]

STOP = set("""a an the and or but if then than that this these those of in on at to for from with
by as is are was were be been being it its it's their there here what which who whom whose how why
when where will would could should may might must can not no nor so such only own same too very
s t just don now over under after before during about against between into through above below up
down out off again further once he she they we you i him her them us his our your my me more most
other some any each few nor own said says say new news latest update updates report reports amid
year years day days week weeks month months first second third top big get gets got make makes""".split())

WORD = re.compile(r"[a-z0-9']+")


def tokens(title):
    return {w for w in WORD.findall(title.lower()) if len(w) > 3 and w not in STOP}


def cluster(items, threshold=0.34, min_shared=3):
    """Group items reporting the same story. Greedy, seeded by recency."""
    groups = []
    for it in items:
        tk = it["_tok"]
        best, best_score = None, 0.0
        for g in groups:
            shared = tk & g["tok"]
            if not shared:
                continue
            union = tk | g["tok"]
            score = len(shared) / len(union) if union else 0.0
            if (score >= threshold or len(shared) >= min_shared) and score > best_score:
                best, best_score = g, score
        if best is None:
            groups.append({"tok": set(tk), "items": [it]})
        else:
            best["items"].append(it)
            # Keep the signature tight: only words the whole group shares.
            best["tok"] &= tk if len(best["tok"] & tk) >= 2 else best["tok"]
    for g in groups:
        g["pubs"] = sorted({(i.get("p") or i["s"]) for i in g["items"]})
        g["items"].sort(key=lambda i: i["_age"])
    groups.sort(key=lambda g: (-len(g["pubs"]), -len(g["items"]), g["items"][0]["_age"]))
    return groups


def best_item(group):
    """Prefer a direct publisher link over a search-engine redirect."""
    direct = [i for i in group["items"] if "news.google.com" not in i["u"]]
    return (direct or group["items"])[0]


def phrase_pubs(pubs, limit=4):
    shown = pubs[:limit]
    rest = len(pubs) - len(shown)
    joined = ", ".join(shown)
    return f"{joined} and {rest} more" if rest > 0 else joined


def age_words(hours):
    if hours < 1:
        return "in the last hour"
    if hours < 24:
        return f"about {round(hours)} hours ago"
    days = round(hours / 24)
    return "yesterday" if days == 1 else f"{days} days ago"


def auto_section(key, label, groups, in_window, fallback):
    """Assemble a section from clustered coverage. States its own limits."""
    body, refs = [], []

    if not groups:
        note = "no coverage in window"
        body.append(
            f"No coverage in the last {in_window}h window, and nothing recent enough "
            "to fall back on." if not fallback else
            f"No coverage in the last {in_window}h window.")
        return {"k": key, "label": label, "note": note, "body": body, "refs": refs}

    lead = groups[0]
    lead_item = best_item(lead)
    n_pubs = len(lead["pubs"])

    if fallback:
        opener = (f"No coverage in the last {in_window} hours. The most recent, "
                  f"{age_words(lead_item['_age'])}: ")
    elif n_pubs >= 3:
        opener = "Most corroborated in the window: "
    else:
        opener = "The window's leading item: "

    if n_pubs >= 3:
        tail = (f"Carried by {phrase_pubs(lead['pubs'])} — {n_pubs} outlets on the same story is "
                f"the strongest corroboration signal here.")
    elif n_pubs == 2:
        tail = f"Carried by {phrase_pubs(lead['pubs'])}, and no one else — thinly covered so far."
    else:
        tail = (f"From {lead['pubs'][0]} alone. A single outlet, so treat it as unconfirmed "
                f"until someone else picks it up.")

    body.append(f"{opener}\u201c{lead_item['t']}\u201d. {tail}")

    others = groups[1:6]
    if others:
        parts = []
        for g in others:
            it = best_item(g)
            n = len(g["pubs"])
            parts.append(f"“{it['t']}” ({n} outlet{'s' if n != 1 else ''})")
        body.append("Also running: " + "; ".join(parts) + ".")

    pk = sum(1 for g in groups for i in g["items"] if i.get("o") == "PK")
    intl = sum(1 for g in groups for i in g["items"] if i.get("o") != "PK")
    if key not in ("WORLD",) and (pk or intl):
        body.append(f"Split of the window: {pk} item{'s' if pk != 1 else ''} from Pakistani outlets, "
                    f"{intl} from international ones.")

    for g in groups[:6]:
        it = best_item(g)
        refs.append({"s": (it.get("p") or it["s"]), "t": it["t"], "u": it["u"]})

    n_items = sum(len(g["items"]) for g in groups)
    note = (f"nothing in {in_window}h - most recent below" if fallback
            else f"{n_items} items \u00b7 lead on {n_pubs} outlet{'s' if n_pubs != 1 else ''}")
    return {"k": key, "label": label, "note": note, "body": body, "refs": refs}


def load(path, hours):
    data = json.load(open(path, encoding="utf-8"))
    now = datetime.now(timezone.utc)
    items = []
    for i in data["items"]:
        if not i.get("ts"):
            continue
        i = dict(i)
        i["_age"] = (now - datetime.fromisoformat(i["ts"].replace("Z", "+00:00"))).total_seconds() / 3600
        i["_tok"] = tokens(i["t"])
        items.append(i)
    return data, items


def build_auto(path, hours):
    data, items = load(path, hours)
    sections = []
    for key, label, watch in SECTIONS:
        if watch:
            pool = [i for i in items if watch in (i.get("w") or [])]
        else:
            pool = [i for i in items if i["d"] == key and not (i.get("w") or [])]

        fresh = [i for i in pool if i["_age"] <= hours]
        fallback = False
        if len(fresh) < 3 and watch:
            older = [i for i in pool if i["_age"] > hours]
            if older:
                fresh, fallback = sorted(older, key=lambda i: i["_age"])[:12], True

        fresh.sort(key=lambda i: i["_age"])
        sections.append(auto_section(key, label, cluster(fresh), int(hours), fallback))

    return {
        "written": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "window_hours": int(hours),
        "mode": "auto",
        "sections": sections,
    }


# --------------------------------------------------------------------------
# Optional: a properly written brief, when an API key is available.
# --------------------------------------------------------------------------
EDITORIAL = """You are writing the Daily Brief for a news dashboard. Below is a digest of the
last {hours} hours grouped into six sections.

Write one brief per section, in this exact order, with these exact keys and labels:
  WORLD -> "World Desk"; PAKISTAN -> "Pakistan Desk"; AAZ -> "Asif Ali Zardari"
  PRES -> "The Presidency"; BBZ -> "Bilawal Bhutto Zardari"; ABZ -> "Aseefa Bhutto Zardari"

Rules:
- Two or three short paragraphs for WORLD and PAKISTAN; one or two for each person.
- Plain declarative prose. No bullet lists, no headings, no "In today's news" preamble.
- Say what happened and why it matters, proportionately. Do not invent significance.
- Group related headlines into one thread. Ten stories about one fire are one paragraph.
- Name people, places and numbers precisely.
- Weigh sources out loud. If a claim rests only on small or aggregator outlets and the
  major papers have not touched it, say so and call it unconfirmed.
- A section on FALLBACK material must open by saying there was no coverage in the window,
  then give the most recent developments and state how old they are.
- Never invent a headline, URL, number or quote. Everything traces to a digest line.

Return ONLY valid JSON, no markdown fence:
{{"sections":[{{"k":"WORLD","label":"World Desk","note":"short stat",
  "body":["para","para"],"refs":[{{"s":"Publisher","t":"exact headline","u":"exact url"}}]}}]}}
4-7 refs for WORLD and PAKISTAN, 3-5 per person. Copy headlines and URLs verbatim.

DIGEST:
{digest}
"""


def build_written(digest_text, hours):
    import anthropic
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=model,
        max_tokens=8000,
        messages=[{"role": "user", "content": EDITORIAL.format(hours=int(hours), digest=digest_text)}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    payload = json.loads(text)
    order = [s[0] for s in SECTIONS]
    got = [s["k"] for s in payload["sections"]]
    if got != order:
        raise ValueError(f"section order mismatch: {got}")
    return {
        "written": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "window_hours": int(hours),
        "mode": "written",
        "sections": payload["sections"],
    }


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "news_data.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "summary.json"
    hours = float(sys.argv[3]) if len(sys.argv) > 3 else 24.0

    payload = None
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import subprocess
            digest = subprocess.run(
                [sys.executable, os.path.join(HERE, "make_digest.py"), src, str(hours)],
                capture_output=True, text=True, check=True).stdout
            payload = build_written(digest, hours)
            print(f"summary: written by {os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-4-5')}")
        except Exception as e:
            print(f"summary: AI path failed ({type(e).__name__}: {e}); using the free generator",
                  file=sys.stderr)

    if payload is None:
        payload = build_auto(src, hours)
        print("summary: assembled from coverage clustering (no API key)")

    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  mode={payload['mode']} sections={len(payload['sections'])} -> {out}")


if __name__ == "__main__":
    main()
