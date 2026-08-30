"""Source registry for the Global News Desk dashboard."""

GN = "https://news.google.com/rss/search?q=when:24h+{q}&hl=en-US&gl=US&ceid=US:en"
GNW = "https://news.google.com/rss/search?q=when:7d+{q}&hl=en-US&gl=US&ceid=US:en"

# (name, short_code, url, desk, topic)
# desk: WORLD | PAKISTAN     topic: politics | business | tech
SOURCES = [
    # ---------------- WORLD :: POLITICS / GENERAL ----------------
    ("Reuters",              "REUT", GN.format(q="source:Reuters"), "WORLD", "politics"),
    ("Associated Press",     "AP",   GN.format(q="source:%22Associated+Press%22"), "WORLD", "politics"),
    ("BBC World",            "BBC",  "https://feeds.bbci.co.uk/news/world/rss.xml", "WORLD", "politics"),
    ("Al Jazeera",           "AJZ",  "https://www.aljazeera.com/xml/rss/all.xml", "WORLD", "politics"),
    ("The Guardian",         "GRD",  "https://www.theguardian.com/world/rss", "WORLD", "politics"),
    ("New York Times",       "NYT",  "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "WORLD", "politics"),
    ("Deutsche Welle",       "DW",   "https://rss.dw.com/rdf/rss-en-world", "WORLD", "politics"),
    ("France 24",            "F24",  "https://www.france24.com/en/rss", "WORLD", "politics"),
    ("CNN",                  "CNN",  GN.format(q="source:CNN"), "WORLD", "politics"),
    ("NPR",                  "NPR",  GN.format(q="source:NPR"), "WORLD", "politics"),
    ("Sky News",             "SKY",  "https://feeds.skynews.com/feeds/rss/world.xml", "WORLD", "politics"),
    ("The Independent",      "IND",  "https://www.independent.co.uk/news/world/rss", "WORLD", "politics"),
    ("The Washington Post",  "WAPO", GN.format(q="source:%22The+Washington+Post%22"), "WORLD", "politics"),
    ("The Times of India",   "TOI",  "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", "WORLD", "politics"),
    ("South China Morning Post", "SCMP", GN.format(q="source:%22South+China+Morning+Post%22"), "WORLD", "politics"),

    # ---------------- WORLD :: BUSINESS / MARKETS ----------------
    ("BBC Business",         "BBC",  "https://feeds.bbci.co.uk/news/business/rss.xml", "WORLD", "business"),
    ("Guardian Business",    "GRD",  "https://www.theguardian.com/uk/business/rss", "WORLD", "business"),
    ("NYT Business",         "NYT",  "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "WORLD", "business"),
    ("CNBC Markets",         "CNBC", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", "WORLD", "business"),
    ("Bloomberg",            "BLM",  GN.format(q="source:Bloomberg"), "WORLD", "business"),
    ("Financial Times",      "FT",   GN.format(q="source:%22Financial+Times%22"), "WORLD", "business"),
    ("The Economist",        "ECON", GN.format(q="source:%22The+Economist%22"), "WORLD", "business"),
    ("MarketWatch",          "MW",   "https://feeds.content.dowjones.io/public/rss/mw_topstories", "WORLD", "business"),
    ("Yahoo Finance",        "YF",   "https://finance.yahoo.com/news/rssindex", "WORLD", "business"),
    ("Al Jazeera Economy",   "AJZ",  GN.format(q="source:%22Al+Jazeera%22+(economy+OR+markets+OR+trade+OR+oil)"), "WORLD", "business"),

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
    ("AI Wire",              "AIW",  GN.format(q="%22artificial+intelligence%22+OR+%22AI+model%22"), "WORLD", "tech"),

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
    ("Pakistan Today",       "PKT",  GN.format(q="source:%22Pakistan+Today%22"), "PAKISTAN", "politics"),
    ("Samaa TV",             "SAMA", GN.format(q="source:%22Samaa+TV%22"), "PAKISTAN", "politics"),
    ("Profit (Pakistan)",    "PRFT", GN.format(q="source:%22Profit+by+Pakistan+Today%22"), "PAKISTAN", "business"),

    # ---------------- PAKISTAN :: GLOBAL COVERAGE ----------------
    ("Reuters on Pakistan",  "REUT", GN.format(q="Pakistan+source:Reuters"), "PAKISTAN", "politics"),
    ("BBC on Pakistan",      "BBC",  GN.format(q="Pakistan+source:BBC"), "PAKISTAN", "politics"),
    ("AP on Pakistan",       "AP",   GN.format(q="Pakistan+source:%22Associated+Press%22"), "PAKISTAN", "politics"),
    ("Al Jazeera on Pakistan","AJZ", GN.format(q="Pakistan+source:%22Al+Jazeera%22"), "PAKISTAN", "politics"),
    ("Global Pakistan Wire", "GLOB", GN.format(q="Pakistan"), "PAKISTAN", "politics"),
    ("Pakistan Economy Wire","GLOB", GN.format(q="Pakistan+(economy+OR+IMF+OR+rupee+OR+inflation+OR+%22State+Bank%22+OR+PSX)"), "PAKISTAN", "business"),
    ("Pakistan Tech Wire",   "GLOB", GN.format(q="Pakistan+(technology+OR+startup+OR+AI+OR+fintech+OR+IT+exports)"), "PAKISTAN", "tech"),

    # ---------------- BHUTTO-ZARDARI WATCH ----------------
    # These feeds surface candidates; membership in the watch band is decided
    # by whether the HEADLINE names a principal (see WATCH below).
    ("Zardari Watch",        "AAZ",  GNW.format(q="%22Asif+Ali+Zardari%22+OR+%22President+Zardari%22"), "PAKISTAN", "politics"),
    ("Bilawal Watch",        "BBZ",  GNW.format(q="%22Bilawal+Bhutto%22"), "PAKISTAN", "politics"),
    ("Aseefa Watch",         "ABZ",  GNW.format(q="%22Aseefa+Bhutto%22+OR+%22Asifa+Bhutto%22"), "PAKISTAN", "politics"),
    ("Bhutto-Zardari Wire",  "PPP",  GNW.format(q="%22Bhutto+Zardari%22"), "PAKISTAN", "politics"),
    ("Presidency Wire",      "PPP",  GNW.format(q="%22President+of+Pakistan%22+OR+%22Aiwan-e-Sadr%22"), "PAKISTAN", "politics"),
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
_BBZ = _re.compile(r"\bBilawal\b", _re.I)
_ABZ = _re.compile(r"\b(Aseefa|Asifa)\b", _re.I)
_AAZ_EXPLICIT = _re.compile(r"\b(Asif\s+(Ali\s+)?Zardari|President\s+Zardari|Co-?Chairman\s+Zardari)\b", _re.I)
_ZARDARI = _re.compile(r"\bZardari\b", _re.I)

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
    """Return the principals named in this headline, e.g. ['BBZ']."""
    hits = []
    bbz = bool(_BBZ.search(title))
    abz = bool(_ABZ.search(title))
    # A bare "Zardari" with no first name is the President in normal usage.
    aaz = bool(_AAZ_EXPLICIT.search(title)) or (
        bool(_ZARDARI.search(title)) and not bbz and not abz)
    if aaz:
        # An act of the office reads as Presidency; the rest is Zardari politics.
        hits.append("PRES" if _PRESIDENCY.search(title) else "AAZ")
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


def pk_relevant(title, feed_url, desk):
    """True unless this is a search-feed item on the Pakistan desk that never
    actually mentions Pakistan or a watch principal in its headline."""
    if desk != "PAKISTAN" or "news.google.com" not in feed_url:
        return True
    return bool(PK_TERMS.search(title)) or bool(classify_watch(title))
