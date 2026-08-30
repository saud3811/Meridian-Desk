#!/usr/bin/env python3
"""
Reduce news_data.json to a compact 24h digest grouped by brief section.

The twice-daily brief run reads this instead of 600 raw items, so the writer
sees a clean, deduplicated, section-ordered view of the window.

  python3 make_digest.py [news_data.json] [hours] > digest.txt
"""
import json, re, sys
from datetime import datetime, timezone

SECTIONS = [
    ("WORLD",    "World Desk",             None),
    ("PAKISTAN", "Pakistan Desk",          None),
    ("AAZ",      "Asif Ali Zardari",       "AAZ"),
    ("PRES",     "The Presidency",         "PRES"),
    ("BBZ",      "Bilawal Bhutto Zardari", "BBZ"),
    ("ABZ",      "Aseefa Bhutto Zardari",  "ABZ"),
]

# Per-section cap on lines handed to the writer.
CAP = {"WORLD": 70, "PAKISTAN": 70, "AAZ": 40, "PRES": 40, "BBZ": 40, "ABZ": 40}


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())[:60]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "news_data.json"
    hours = float(sys.argv[2]) if len(sys.argv) > 2 else 24.0
    data = json.load(open(src))
    now = datetime.now(timezone.utc)

    fresh = []
    for i in data["items"]:
        if not i.get("ts"):
            continue
        age = (now - datetime.fromisoformat(i["ts"].replace("Z", "+00:00"))).total_seconds() / 3600
        if age <= hours:
            i = dict(i)
            i["age"] = age
            fresh.append(i)

    print(f"DIGEST | generated {data['generated']} | window {hours:g}h | "
          f"{len(fresh)} items in window of {len(data['items'])} held")
    print()

    def collect(pool, key, watch):
        if watch:
            rows = [i for i in pool if watch in (i.get("w") or [])]
        else:
            rows = [i for i in pool if i["d"] == key and not (i.get("w") or [])]
        rows.sort(key=lambda i: i["age"])
        seen, uniq = set(), []
        for r in rows:
            k = norm(r["t"])
            if k in seen:
                continue
            seen.add(k)
            uniq.append(r)
        return uniq

    def emit(rows, cap):
        for r in rows[:cap]:
            src_name = r.get("p") or r["s"]
            print(f"  [{r['age']:4.1f}h] [{r.get('o','')}] [{r['k'][:4]}] {src_name} :: {r['t']}")
            print(f"           {r['u']}")
        if len(rows) > cap:
            print(f"  ... {len(rows)-cap} more not listed")

    # Everything held, with ages, for the sparse-section fallback.
    allitems = []
    for i in data["items"]:
        if not i.get("ts"):
            continue
        i = dict(i)
        i["age"] = (now - datetime.fromisoformat(i["ts"].replace("Z", "+00:00"))).total_seconds() / 3600
        allitems.append(i)

    for key, label, watch in SECTIONS:
        uniq = collect(fresh, key, watch)
        pk = sum(1 for r in uniq if r.get("o") == "PK")
        print(f"===== {key} :: {label} :: {len(uniq)} items "
              f"({pk} Pakistani / {len(uniq)-pk} international) =====")
        if not uniq:
            print("  (nothing in this window)")
        emit(uniq, CAP.get(key, 40))

        # A principal can go days without coverage. Rather than printing
        # "nothing" every day, show the most recent developments and label
        # them clearly as older than the window.
        if watch and len(uniq) < 3:
            older = [r for r in collect(allitems, key, watch) if r["age"] > hours]
            if older:
                print(f"  --- FALLBACK: no{'' if uniq else ''} recent coverage in window; "
                      f"most recent {min(len(older), 12)} beyond {hours:g}h ---")
                emit(older, 12)
        print()


if __name__ == "__main__":
    main()
