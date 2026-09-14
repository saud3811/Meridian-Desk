"""Source registry for the Global News Desk dashboard."""


# (name, short_code, url, desk, topic)
# desk: WORLD | PAKISTAN     topic: politics | business | tech
SOURCES = [
    # ---------------- WORLD :: POLITICS / GENERAL ----------------
    ("BBC World",            "BBC",  "https://feeds.bbci.co.uk/news/world/rss.xml", "WORLD", "politics"),
    ("Al Jazeera",           "AJZ",  "https://www.aljazeera.com/xml/rss/all.xml", "WORLD", "politics"),
    ("The Guardian",         "GRD",  "https://www.theguardian.com/world/rss", "WORLD", "politics"),
    ("New York Times",       "NYT",  "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "WORLD", "politics"),
    ("Deutsche Welle",       "DW",   "https://rss.dw.com/rdf/rss-en-world", "WORLD", "politics"),
    ("France 24",            "F24",  "https://www.france24.com/en/rss", "WORLD", "politics"),
    ("Sky News",             "SKY",  "https://feeds.skynews.com/feeds/rss/world.xml", "WORLD", "politics"),
    ("The Independent",      "IND",  "https://www.independent.co.uk/news/world/rss", "WORLD", "politics"),
    ("The Times of India",   "TOI",  "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", "WORLD", "politics"),

    # ---------------- WORLD :: BUSINESS / MARKETS ----------------
    ("BBC Business",         "BBC",  "https://feeds.bbci.co.uk/news/business/rss.xml", "WORLD", "business"),
    ("Guardian Business",    "GRD",  "https://www.theguardian.com/uk/business/rss", "WORLD", "business"),
    ("NYT Business",         "NYT",  "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "WORLD", "business"),
    ("CNBC Markets",         "CNBC", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", "WORLD", "business"),
    ("MarketWatch",          "MW",   "https://feeds.content.dowjones.io/public/rss/mw_topstories", "WORLD", "business"),
    ("Yahoo Finance",        "YF",   "https://finance.yahoo.com/news/rssindex", "WORLD", "business"),

    # ---------------- WORLD :: TECH / AI ----------------
    ("BBC Technology",       "BBC",  "https://feeds.bbci.co.uk/news/technology/rss.xml", "WORLD", "tech"),
    ("Guardian Tech",        "GRD",  "https://www.theguardian.com/uk/technology/rss", "WORLD", "tech"),
    ("NYT Technology",       "NYT",  "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "WORLD", "tech"),
    ("TechCrunch",           "TC",   "https://techcrunch.com/feed/", "WORLD", "tech"),
    ("The Verge",            "VRG",  "https://www.theverge.com/rss/index.xml", "WORLD", "tech"),
    ("Ars Technica",         "ARS",  "https://feeds.arstechnica.com/arstechnica/index", "WORLD", "tech"),
    ("Wired",                "WRD",  "https://www.wired.com/feed/rss", "WORLD", "tech"),
    ("MIT Tech Review",      "MIT",  "https://www.technologyreview.com/feed/", "WORLD", "tech"),
    ("Hacker News",          "HN",   "https://hnrss.org/frontpage", "WORLD", "tech"),

    # ---------------- PAKISTAN :: NATIONAL ----------------
    ("Dawn",                 "DAWN", "https://www.dawn.com/feeds/home", "PAKISTAN", "politics"),
    ("Dawn Pakistan",        "DAWN", "https://www.dawn.com/feeds/pakistan", "PAKISTAN", "politics"),
    ("Dawn Business",        "DAWN", "https://www.dawn.com/feeds/business", "PAKISTAN", "business"),
    ("Dawn World",           "DAWN", "https://www.dawn.com/feeds/world", "PAKISTAN", "politics"),
    ("Geo News",             "GEO",  "https://www.geo.tv/rss/1/1", "PAKISTAN", "politics"),
    ("Geo Business",         "GEO",  "https://www.geo.tv/rss/1/3", "PAKISTAN", "business"),
    ("Geo Sci-Tech",         "GEO",  "https://www.geo.tv/rss/1/53", "PAKISTAN", "tech"),
    ("Express Tribune",      "TRIB", "https://tribune.com.pk/feed/home", "PAKISTAN", "politics"),
    ("Tribune Business",     "TRIB", "https://tribune.com.pk/feed/business", "PAKISTAN", "business"),
    ("Tribune Pakistan",     "TRIB", "https://tribune.com.pk/feed/pakistan", "PAKISTAN", "politics"),
    ("ARY News",             "ARY",  "https://arynews.tv/feed/", "PAKISTAN", "politics"),
    ("Business Recorder",    "BR",   "https://www.brecorder.com/feeds/latest-news", "PAKISTAN", "business"),
    ("BR Markets",           "BR",   "https://www.brecorder.com/feeds/markets", "PAKISTAN", "business"),
    ("The News International","NEWS", "https://www.thenews.com.pk/rss/1/1", "PAKISTAN", "politics"),
    ("The News Business",    "NEWS", "https://www.thenews.com.pk/rss/1/3", "PAKISTAN", "business"),
    ("The Nation",           "NATN", "https://www.nation.com.pk/rss/latest", "PAKISTAN", "politics"),
    ("Bol News",             "BOL",  "https://www.bolnews.com/feed/", "PAKISTAN", "politics"),

    # ---------------- PAKISTAN :: GLOBAL COVERAGE ----------------

    # ---------------- BHUTTO-ZARDARI WATCH ----------------
    # These feeds surface candidates; membership in the watch band is decided
    # by whether the HEADLINE names a principal (see WATCH below).
]

# Feeds that publish high-volume opinion/columns; keep their share small.
CAPS = {
    "The Nation": 4,
    "Hacker News": 5,
    "Global Pakistan Wire": 12,
}

import re as _re

# ---------------------------------------------------------------------------
# Bhutto-Zardari watch
#
# A story joins the watch band only when the HEADLINE names a principal.
# Matching on body text instead would fill the band with stories that merely
# mention them in passing.
# ---------------------------------------------------------------------------
# Latin script
_BBZ = _re.compile(r"\bBilawal\b", _re.I)
_ABZ = _re.compile(r"\b(Aseefa|Asifa|Asefa)\b", _re.I)
_AAZ_EXPLICIT = _re.compile(
    r"\b(Asif\s+(Ali\s+)?Zardari|President\s+Zardari|Co-?Chairman\s+Zardari)\b", _re.I)
_ZARDARI = _re.compile(r"\bZardari\b", _re.I)

# Urdu and Arabic script.
#
# GDELT matches on machine translation but returns the ORIGINAL headline, so a
# query written in English hands back Urdu and Arabic titles. Without these
# patterns those articles reach the Pakistan desk and never reach the watch —
# which would quietly gut the thing this dashboard exists for.
#
# Note the two forms of final ya: Urdu writes زرداری, Arabic writes زرداري.
# Note also that آصف (Asif) is a prefix of آصفہ (Aseefa), so Aseefa is tested
# first and Asif is only accepted when followed by علی / علي.
_BBZ_NAT = _re.compile(r"بلاول")
_ABZ_NAT = _re.compile(r"آصفہ|آصفة|آصفه|عاصفہ")
_ZARDARI_NAT = _re.compile(r"زرداری|زرداري")
_AAZ_NAT = _re.compile(r"آصف\s*عل[یي]|صدر\s*زرداری|الرئيس\s*زرداري")
_PRES_NAT = _re.compile(r"صدر|الرئيس|ایوان\s*صدر|ایوانِ\s*صدر|رئاسة|رئيس\s*باكستان")

# Presidential-office language. A Zardari story that speaks in these terms is
# about the office; anything else about him is party or personal.
_PRESIDENCY = _re.compile(
    r"(aiwan-?e-?sadr|presidency|president\s+house|presidential\s+\w+|"
    r"\bsigns?\b|\bsigned\b|assent|ordinance|\bbill\b|summons?|prorogue|"
    r"state\s+visit|credentials|\benvoy\b|ambassador|sworn\s+in|oath|"
    r"clemency|pardon|address(?:es|ed)?\s+(?:the\s+)?(?:joint\s+)?(?:session|parliament)|"
    r"condol|felicitat|grief|sorrow|message\s+on|approves?|ratif)", _re.I)

WATCH = [
    ("AAZ",  "Asif Ali Zardari",       "PPP co-chairman &amp; politics"),
    ("PRES", "The Presidency",         "Aiwan-e-Sadr &amp; official acts"),
    ("BBZ",  "Bilawal Bhutto Zardari", "PPP chairman"),
    ("ABZ",  "Aseefa Bhutto Zardari",  "First Lady"),
]


def classify_watch(title):
    """Return the principals named in this headline, in any supported script."""
    hits = []
    bbz = bool(_BBZ.search(title) or _BBZ_NAT.search(title))
    abz = bool(_ABZ.search(title) or _ABZ_NAT.search(title))

    aaz_explicit = bool(_AAZ_EXPLICIT.search(title) or _AAZ_NAT.search(title))
    bare_zardari = bool(_ZARDARI.search(title) or _ZARDARI_NAT.search(title))
    # A bare "Zardari" with no first name is the President in normal usage,
    # but when Bilawal or Aseefa is named the surname belongs to them.
    aaz = aaz_explicit or (bare_zardari and not bbz and not abz)

    if aaz:
        # An act of the office reads as Presidency; the rest is Zardari politics.
        office = bool(_PRESIDENCY.search(title)) or bool(_PRES_NAT.search(title))
        hits.append("PRES" if office else "AAZ")
    if bbz:
        hits.append("BBZ")
    if abz:
        hits.append("ABZ")
    return hits


# ---------------------------------------------------------------------------
# Pakistani vs international media
# ---------------------------------------------------------------------------
PK_FEEDS = {
    "Dawn", "Dawn Pakistan", "Dawn Business", "Dawn World", "Geo News",
    "Geo Business", "Geo Sci-Tech", "Express Tribune", "Tribune Business",
    "Tribune Pakistan", "ARY News", "Business Recorder", "BR Markets",
    "The News International", "The News Business", "The Nation", "Bol News",
    "Pakistan Today", "Samaa TV", "Profit (Pakistan)",
}

_PK_PUB = _re.compile(
    r"(dawn|geo\b|geo\.tv|geo news|express tribune|tribune\.com|ary\b|arynews|"
    r"business recorder|brecorder|the news|thenews|nation\.com|the nation|bol news|bolnews|"
    r"pakistan today|samaa|profit|dunya|92 news|aaj\b|jang|nawaiwaqt|daily times|"
    r"minute mirror|daily ausaf|ausaf|pakistan observer|friday times|hum news|"
    r"neo (tv|news)|gnn|suno news|capital tv|ptv|app\b|associated press of pakistan|"
    r"pakistan connect|global village space|the current|24 news|city42|abb takk|"
    r"such tv|urdu point|urdupoint|pakistan press|paktribune)", _re.I)


def classify_origin(feed_name, publisher):
    """PK for Pakistani outlets, INTL for everyone else."""
    if publisher:
        return "PK" if _PK_PUB.search(publisher) else "INTL"
    return "PK" if feed_name in PK_FEEDS else "INTL"


# ---------------------------------------------------------------------------
# Relevance guard for open-web search feeds on the Pakistan desk.
#
# A query like `Pakistan source:"Associated Press"` also returns AP stories that
# merely brush past Pakistan. Search-derived items must earn their place on the
# desk by naming Pakistan (or a principal) in the headline itself.
# ---------------------------------------------------------------------------
PK_TERMS = _re.compile(
    r"\b(pakistan\w*|islamabad|karachi|lahore|peshawar|quetta|rawalpindi|multan|"
    r"faisalabad|sindh|punjab|balochistan|khyber|gilgit|kashmir|"
    r"imran\s+khan|shehbaz|zardari|bilawal|aseefa|asifa|munir|"
    r"pti|ppp|pml-?n|psx|kse-?100|rupee|state\s+bank|nadra|isi|"
    r"lord'?s|test\s+series)\b", _re.I)

# The same test in Urdu and Arabic script. Without this, an Arabic-language
# query for Pakistan returns regional stories — Hormuz, Sudan, Egypt — that
# have nothing to do with Pakistan and would sit on the Pakistan desk as noise.
PK_TERMS_NAT = _re.compile(
    r"پاکستان|باكستان|باکستان|اسلام\s*آباد|إسلام\s*آباد|کراچی|كراتشي|"
    r"لاہور|لاهور|پشاور|بلوچستان|سندھ|پنجاب|کشمیر|كشمير|"
    r"زرداری|زرداري|بلاول|آصفہ|آصفة|عمران\s*خان|شہباز|شهباز")


def is_pk_relevant(title):
    """True when a headline actually concerns Pakistan, in any script."""
    return bool(PK_TERMS.search(title) or PK_TERMS_NAT.search(title)
                or classify_watch(title))


def pk_relevant(title, feed_url, desk):
    """True unless this is a search-feed item on the Pakistan desk that never
    actually mentions Pakistan or a watch principal in its headline."""
    if desk != "PAKISTAN" or "news.google.com" not in feed_url:
        return True
    return bool(PK_TERMS.search(title)) or bool(classify_watch(title))


# ---------------------------------------------------------------------------
# GDELT queries
#
# GDELT is now the primary source; the RSS list above is the backup layer.
#
# The key discovery that shapes this: GDELT matches against machine-translated
# text but returns the ORIGINAL headline. One English query for the family
# therefore brings back Urdu, Hindi and Arabic coverage with native titles —
# which is why the watch needs only one query rather than one per language.
#
# Keep this list short. GDELT rate-limits hard, and every query is a chance to
# be throttled. Five is the budget.
#
# (key, label, code, query, mode, timespan, desk, topic)
# ---------------------------------------------------------------------------
GDELT_QUERIES = [
    # THE MAIN EVENT — all four principals in one query, all languages.
    ("watch", "GDELT Zardari Watch", "GDLT",
     '("Asif Ali Zardari" OR "Bilawal Bhutto" OR "Aseefa Bhutto" OR '
     '"President Zardari" OR "Bhutto Zardari")',
     "artlist", "7d", "PAKISTAN", "politics"),

    # The family as the Arab press covers them.
    ("watch_ar", "GDELT Watch (Arabic)", "GDAR",
     '(Zardari OR Bilawal) sourcelang:arabic',
     "artlist", "7d", "PAKISTAN", "politics"),

    # Pakistani outlets, English and Urdu together.
    ("pakistan", "GDELT Pakistan Desk", "GDPK",
     'Pakistan sourcecountry:pakistan',
     "artlist", "24h", "PAKISTAN", "politics"),

    # Gulf / MENA coverage of Pakistan.
    #
    # Anchored on the ARABIC word for Pakistan. The English term plus a
    # language filter matched loosely and returned Hormuz, Yemen and Egypt
    # stories that had nothing to do with Pakistan.
    ("gulf", "GDELT Gulf & MENA", "GDME",
     '"باكستان"',
     "artlist", "48h", "PAKISTAN", "politics"),

    # Coverage volume for the watch sparkline (not articles).
    ("volume", "GDELT Watch Volume", "GDVOL",
     '("Asif Ali Zardari" OR "Bilawal Bhutto" OR "Aseefa Bhutto" OR "President Zardari")',
     "timelinevol", "7d", None, None),
]

# Language label -> short badge shown on a row.
LANG_BADGE = {
    "English": "EN", "Urdu": "UR", "Arabic": "AR", "Hindi": "HI",
    "Persian": "FA", "Turkish": "TR", "Chinese": "ZH", "French": "FR",
    "Spanish": "ES", "German": "DE", "Russian": "RU", "Pashto": "PS",
    "Bengali": "BN", "Indonesian": "ID", "Malay": "MS",
}

# Gulf / MENA source countries, for the regional tag.
MENA = {
    "United Arab Emirates", "Saudi Arabia", "Qatar", "Kuwait", "Bahrain",
    "Oman", "Egypt", "Jordan", "Lebanon", "Iraq", "Syria", "Yemen",
    "Palestinian Territory", "Israel", "Libya", "Tunisia", "Algeria",
    "Morocco", "Sudan", "Iran", "Turkey",
}


def region_of(country, lang):
    """PK | MENA | INTL — where a story is being told from."""
    if country == "Pakistan":
        return "PK"
    if country in MENA or lang == "Arabic":
        return "MENA"
    return "INTL"
