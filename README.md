# Meridian News Desk

A self-hosting news terminal built around a **Bhutto–Zardari watch** — Asif Ali
Zardari, the Presidency, Bilawal and Aseefa — with world and Pakistan desks
either side of it, and a daily brief.

Coverage comes from **GDELT** (primary) and direct RSS (backup), in **English,
Urdu and Arabic**. It rebuilds itself on a schedule and deploys to GitHub Pages.

No server. No database. No API keys required. Free to run indefinitely.

News data courtesy of [The GDELT Project](https://www.gdeltproject.org/), free
for any use with attribution.

---

## Deploy it in about five minutes

You need a GitHub account. Everything else is free.

### 1. Create an empty repository

Go to [github.com/new](https://github.com/new). Give it a name — `meridian-desk`
works. Make it **Public** (GitHub Pages and unlimited Actions minutes are free
only on public repos). **Do not** tick "Add a README", "Add .gitignore" or
"Choose a license" — this folder already has them, and a pre-filled repo makes
the first push conflict.

### 2. Push this folder to it

From inside this folder, run these four commands. Replace `YOU` with your GitHub
username and `meridian-desk` with your repo name if you chose a different one.

```bash
git init -b main
git add -A
git commit -m "Meridian News Desk"
git remote add origin https://github.com/YOU/meridian-desk.git
git push -u origin main
```

If git asks who you are, set it once and re-run the commit:

```bash
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
```

If the push asks for a password, GitHub no longer accepts account passwords.
Create a token at **github.com → Settings → Developer settings → Personal access
tokens → Tokens (classic)**, tick the `repo` and `workflow` scopes, and paste the
token as the password.

### 3. Turn on Pages

In your new repo: **Settings → Pages → Build and deployment → Source**, and
choose **GitHub Actions**. Not "Deploy from a branch" — the workflow publishes
directly.

### 4. Run it once

**Actions → Refresh and deploy → Run workflow.** The first run takes about four
minutes, most of it fetching feeds. When it finishes, your dashboard is live at:

```
https://YOU.github.io/meridian-desk/
```

That URL works in any browser on any device — phone, laptop, someone else's
machine. Bookmark it. From then on it rebuilds itself every two hours.

If the Actions tab shows a red run, open it and read the failing step. The most
common cause by far is step 3 not being done yet.

---

## What runs, and when

The workflow in `.github/workflows/refresh.yml` fires:

- **every 2 hours**, on a cron
- **whenever you push** to `main`
- **on demand**, from the Actions tab

Each run pulls every feed, writes the brief, rebuilds the page and deploys it.

Two details worth knowing about GitHub's scheduler. Cron runs are best-effort and
can be delayed by 5–20 minutes when GitHub is busy — this is normal and not a
fault in the workflow. And GitHub disables scheduled workflows in repos with no
activity for 60 days; the workflow writes a one-line heartbeat commit on each run
specifically to prevent that. If it ever does get disabled you will get an email
with a button to re-enable it.

### Changing the schedule

Edit the `cron` line. It is in **UTC**, so subtract 5 hours from Pakistan time.

```yaml
- cron: "0 */2 * * *"   # every 2 hours (default)
- cron: "0 * * * *"     # hourly
- cron: "0 2 * * *"     # once daily at 07:00 PKT
- cron: "0 2,15 * * *"  # twice daily at 07:00 and 20:00 PKT
```

Hourly is still free on a public repo — Actions minutes are unmetered there.

---

## Where the news comes from

**GDELT is primary.** One query covers all four principals, and because GDELT
matches against machine-translated text but returns the *original* headline,
that single English query brings back Urdu, Hindi and Arabic coverage with
native titles. That is why the watch needs one query rather than one per
language, and why the name matcher in `sources.py` handles Arabic script as
well as Latin.

**Direct RSS is the backup layer** — Dawn, Geo, Tribune, ARY, Business Recorder,
BBC, Guardian, NYT, Al Jazeera and others. These were the feeds that survived
when Google News blocked GitHub's runners; every Google News query was dropped
because all 26 of them died at once.

### Two GDELT behaviours the code defends against

**It soft-throttles with an empty 200, not a 429.** A query returning 53
articles returned 0 an hour later, then worked again. So an empty live result is
never treated as truth: it will not overwrite a cached payload, and the cached
one is served instead. Without this the watch empties silently — which is
exactly how it broke the first time.

**Rate limits are real and undocumented.** The query budget is five per run,
spaced, with exponential backoff. Results are cached in `data/`, which the
workflow persists between runs via `actions/cache`, and a seed cache is
committed so even a first run on a cold machine has something to show.

The dashboard states its own provenance: the footer reports how many items came
from GDELT versus RSS and how many queries were served from cache.

## The daily brief

The Summary button opens a brief covering the last 24 hours in six sections:
World Desk, Pakistan Desk, and one each for Asif Ali Zardari, the Presidency,
Bilawal Bhutto Zardari and Aseefa Bhutto Zardari.

It works in two modes, and the panel always says which one you are looking at.

**Assembled** (default, free, no key). `make_summary.py` clusters each section's
headlines and ranks the clusters by how many *distinct publishers* carried the
same story. Corroboration is the one quality signal available without editorial
judgement: a story nine outlets ran independently leads the section, and a story
only one outlet has is flagged as unconfirmed. It reads as structured findings
rather than prose, and it never invents anything.

**Written** (optional, costs a few cents per run). Add your Anthropic API key at
**Settings → Secrets and variables → Actions → New repository secret**, named
`ANTHROPIC_API_KEY`. The next run composes a proper written brief instead. To
pin a specific model, add a repository *variable* named `ANTHROPIC_MODEL`.

The upgrade is automatic and the fallback is safe: if the API errors, rate-limits
or the key expires, that run silently reverts to the assembled brief rather than
failing the deploy.

---

## Local development

Python 3.9 or newer.

```bash
pip install -r requirements.txt

python src/fetch_news.py data/news_data.json          # pull the feeds (~3 min)
python src/make_summary.py data/news_data.json data/summary.json 24
python src/build.py                                   # -> dist/index.html

python -m http.server -d dist 8000                    # then open localhost:8000
```

To see the raw material a brief is written from:

```bash
python src/make_digest.py data/news_data.json 24
```

---

## Layout

| Path | What it is |
|---|---|
| `src/gdelt.py` | GDELT client — backoff, caching, and the empty-result guard. |
| `src/sources.py` | GDELT queries, RSS registry, and the multilingual classifiers. |
| `src/fetch_news.py` | Pulls every feed concurrently, dedupes, normalises. |
| `src/make_digest.py` | Reduces a pull to a 24h digest grouped by section. |
| `src/make_summary.py` | Produces the brief — assembled, or written when a key is set. |
| `src/build.py` | Injects data into the template, writes `dist/index.html`. |
| `src/template.html` | The whole interface. One file, no build step, no dependencies. |
| `.github/workflows/refresh.yml` | The schedule, the build and the deploy. |
| `data/` | Build outputs. Only the heartbeat file is committed. |

The deployed page is a single self-contained HTML file. Everything it needs is
inside it, so it loads fast, works offline once cached, and can be saved and
mailed to someone as-is.

---

## Customising

### Adding a feed

Add a row to `SOURCES` in `src/sources.py`:

```python
("Display name", "CODE", "https://example.com/feed.xml", "WORLD", "politics"),
```

`CODE` is the short badge on each row (4–5 characters reads best). The fourth
field is the desk, `WORLD` or `PAKISTAN`. The fifth is the fallback beat —
`politics`, `business` or `tech` — used only when no keyword matches the
headline.

If a publisher batch-publishes opinion columns, cap its share in the `CAPS`
dictionary in the same file, or it will crowd out reported news.

### Tuning the GDELT queries

`GDELT_QUERIES` in `src/sources.py` holds all five. Keep the list short — every
query is a chance to be throttled. Two syntax rules learned the hard way:
OR'd terms must be wrapped in parentheses, and operator-only queries return
nothing, so always include at least one keyword.

Anchor language queries in that language. `Pakistan sourcelang:arabic` matched
loosely and returned Hormuz and Sudan stories; `"باكستان"` does not.

### Tracking a different person

Add a name pattern to `classify_watch()` and an entry to `WATCH` in
`src/sources.py`, add a matching column to `PRINCIPALS` in `src/template.html`,
and add the section to `SECTIONS` in both `make_digest.py` and `make_summary.py`.

---

## How it decides things

These rules are what stop the page from being a raw RSS dump.

**Multilingual matching.** The watch matcher reads Latin, Urdu and Arabic
script. Two traps are handled explicitly: Urdu writes زرداری with a different
final ya than Arabic زرداري, and آصف (Asif) is a prefix of آصفہ (Aseefa), so
Aseefa is tested first and Asif only counts when followed by علی/علي.

**Relevance.** Anything on the Pakistan desk must name Pakistan or a principal
in its headline, in any script. Without this, Arabic-language queries fill the
desk with regional news that merely shares a search term.

**Ordering.** Strict reverse chronology, with one adjustment: no publisher may
take more than two consecutive rows. A paper that batch-publishes its opinion
columns at 6pm cannot otherwise swallow a whole column. Nothing is scored or
ranked for "engagement".

**Beats.** Assigned by keyword from the headline itself, not by which feed
carried it. A West Bank story arriving through a business feed is still politics.

**The watch band.** A story joins it only when a principal is named in the
*headline*. Matching on body text fills the band with stories that mention them
in passing. A bare "Zardari" with no first name is read as the President; when
"Bilawal" or "Aseefa" appears in the same headline, the surname is treated as
part of their name.

**Presidency vs politics.** Signing bills, receiving ambassadors and state visits
are presidential business; party matters and family news are Zardari the
politician. The classifier decides by the language in the headline.

**PK vs INTL.** Tagged by the outlet that actually published the item, read from
the feed's publisher metadata rather than guessed from the feed name.

**Relevance guard.** Open-web search feeds on the Pakistan desk must name Pakistan
or a principal in the headline. Without this, a query like
`Pakistan source:"Associated Press"` drops unrelated AP stories onto the desk.

**Clock skew.** Some publishers stamp their items ahead of UTC. Each feed is
shifted back by its own measured offset, so a paper with a wrong clock does not
permanently occupy the top of the page.

---

## Cost and limits

Free, on a public repository:

- **GitHub Pages** — free hosting, 100 GB/month bandwidth, 1 GB site limit. This
  site is under half a megabyte.
- **GitHub Actions** — unmetered minutes on public repos.
- **The feeds** — public RSS, no keys, no quotas. Publishers rate-limit
  occasionally; the fetcher retries three times and a handful of empty feeds on
  any given run is normal.

The only optional cost is the Anthropic API key, and only if you choose to add one.

On a **private** repo, Pages requires GitHub Pro and Actions is capped at 2,000
minutes/month — around 8 runs a day at ~4 minutes each. Drop the schedule to
`0 2,15 * * *` if you go that route.

---

## Troubleshooting

**The Actions run is red.** Open the run and read the failing step name. If it is
the deploy step, Pages is probably not set to "GitHub Actions" yet (step 3).

**"degraded pull — keeping the previous deploy live".** Working as designed. The
run fetched too few items to be trustworthy and refused to overwrite a good build
with a bad one. The next scheduled run will almost always succeed.

**Some feeds show as empty in the log.** Normal. Publishers rate-limit and a few
feeds return nothing on any given pull. If a feed is empty on *every* run, its URL
has probably moved — check it in a browser.

**The page is live but stale.** Check the Actions tab. If the last run is more
than a few hours old, the schedule may have been disabled for inactivity — GitHub
will have emailed you a re-enable link.

**The brief says "not yet written".** `make_summary.py` did not run or produced
nothing. Check that step in the workflow log.

---

## Licence

MIT — see `LICENSE`. The code is yours to do anything with. The headlines are not:
this project stores no article text and claims nothing over the material it links
to. Every headline remains the property of its publisher, and every link goes
straight to them.
