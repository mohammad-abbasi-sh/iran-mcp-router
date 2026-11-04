"""Deterministic, dependency-free router over the iran-mcp server catalog.

Given a task in Persian or English, :func:`route` returns the best matching
iran-mcp MCP servers: which server to install, which tool to call first, and
why. No network, no models, no dependencies -- pure stdlib keyword routing
with Persian-aware text normalization.

The catalog data (server names, tools, install commands) comes from
data/catalog.json, generated from iran-mcp's public servers.json.
"""

import json
import os
import re
import unicodedata

CATALOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "catalog.json"
)

# Arabic codepoints that Persian writers often type by accident.
_AR2FA = str.maketrans({"ي": "ی", "ك": "ک", "ة": "ه", "ؤ": "و", "إ": "ا", "أ": "ا"})
# Persian + Arabic-Indic digits -> ASCII (NFKC does not fold these).
_FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

# Cache of compiled word-boundary patterns per normalized keyword.
_PATTERNS = {}


def normalize_fa(text):
    """Normalize Persian/Arabic-script text for keyword matching.

    - NFKC: folds full-width chars and compatibility forms
    - Arabic ي/ك/ة -> Persian ی/ک/ه ; Persian/Arabic-Indic digits -> ASCII
    - ZWNJ/ZWJ removed (می‌خواهم and میخواهم match the same way)
    - whitespace collapsed, lowercased, stripped
    """
    if not isinstance(text, str):
        text = str(text)
    t = unicodedata.normalize("NFKC", text)
    t = t.translate(_AR2FA).translate(_FA_DIGITS)
    t = t.replace("‌", "").replace("‍", "")
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


# ---------------------------------------------------------------------------
# Routing knowledge (hand-authored, original). Server keywords weigh 3,
# name aliases weigh 4, category keywords weigh 1.
# Every suggested tool name below was verified against the real catalog.
# ---------------------------------------------------------------------------

SERVER_RULES = [
    {
        "id": "tgju-mcp",
        "aliases": ["tgju", "تیجیو"],
        "keywords": [
            "سکه", "امامی", "بهار آزادی", "نیم سکه", "ربع سکه", "تمام سکه",
            "طلا", "دلار", "ارز", "یورو", "درهم", "لیر", "پوند", "مظنه",
            "قیمت ارز", "نرخ ارز", "coin", "gold price", "dollar", "currency",
            "exchange rate",
        ],
        "tool": "tj_get_prices",
        "intent_tools": {"overview": "tj_market_summary", "history": "tj_price_history"},
    },
    {
        "id": "milligold-mcp",
        "aliases": ["milligold", "میلیگلد", "میلی‌گلد"],
        "keywords": ["طلای آبشده", "آبشده", "مظنه آبشده", "melted gold"],
        "tool": "mg_get_price",
        "intent_tools": {"history": "mg_price_history"},
    },
    {
        "id": "iran-gold-mcp",
        "aliases": [],
        "keywords": ["مقایسه قیمت طلا", "قیمت طلا در صرافی‌ها"],
        "tool": "gold_prices",
        "intent_tools": {},
    },
    {
        "id": "torob-mcp",
        "aliases": ["torob", "ترب"],
        "keywords": [
            "قیمت گوشی", "موبایل", "گوشی", "مقایسه قیمت فروشگاه", "ارزانترین فروشگاه",
            "قیمت لپ تاپ", "قیمت لپ‌تاپ", "price comparison",
        ],
        "tool": "tb_search",
        "intent_tools": {
            "cheapest": "tb_cheapest",
            "history": "tb_price_chart",
            "compare": "tb_compare",
        },
    },
    {
        "id": "digikala-mcp",
        "aliases": ["digikala", "دیجی‌کالا", "دیجیکالا"],
        "keywords": ["دیجی کالا", "خرید اینترنتی", "online shop"],
        "tool": "dk_search",
        "intent_tools": {"cheapest": "dk_find_cheapest"},
    },
    {
        "id": "emalls-ir-mcp",
        "aliases": ["emalls", "ایمالز"],
        "keywords": ["ایمالز"],
        "tool": "em_search",
        "intent_tools": {"compare": "em_compare", "history": "em_price_history"},
    },
    {
        "id": "mobile-ir-mcp",
        "aliases": ["mobile.ir"],
        "keywords": ["مشخصات گوشی", "mobile.ir"],
        "tool": "mi_search",
        "intent_tools": {"compare": "mi_compare"},
    },
    {
        "id": "technolife-mcp",
        "aliases": ["technolife", "تکنولایف"],
        "keywords": ["تکنولایف"],
        "tool": "tl_category_products",
        "intent_tools": {},
    },
    {
        "id": "khanoumi-mcp",
        "aliases": ["khanoumi", "خانومی"],
        "keywords": ["خانومی", "لوازم آرایشی", "cosmetics"],
        "tool": "kh_search",
        "intent_tools": {"cheapest": "kh_find_cheapest"},
    },
    {
        "id": "banimode-mcp",
        "aliases": ["banimode", "بانی مد"],
        "keywords": ["بانی مد", "fashion"],
        "tool": "bm_search",
        "intent_tools": {},
    },
    {
        "id": "divar-mcp",
        "aliases": ["divar", "دیوار"],
        "keywords": ["دیوار", "آگهی", "نیازمندی", "classified", "divar"],
        "tool": "dv_search",
        "intent_tools": {},
    },
    {
        "id": "sheypoor-mcp",
        "aliases": ["sheypoor", "شیپور"],
        "keywords": ["شیپور", "sheypoor"],
        "tool": "sp_search",
        "intent_tools": {},
    },
    {
        "id": "mrbilit-mcp",
        "aliases": ["mrbilit", "مستربلیط"],
        "keywords": [
            "بلیط هواپیما", "بلیط اتوبوس", "بلیط قطار", "مستربلیط",
            "flight", "flights",
        ],
        "tool": "mb_search_flights",
        "intent_tools": {},
    },
    {
        "id": "alibaba-ir-mcp",
        "aliases": ["alibaba", "علی بابا"],
        "keywords": ["علی بابا", "هتل", "تور", "اقامتگاه", "hotel", "tour", "villa"],
        "tool": "al_hotels",
        "intent_tools": {"cheapest": "al_tours_cheapest"},
    },
    {
        "id": "jabama-mcp",
        "aliases": ["jabama", "جاباما"],
        "keywords": ["جاباما", "کنسرت", "تئاتر", "سینما", "concert", "theater"],
        "tool": "jb_search_events",
        "intent_tools": {},
    },
    {
        "id": "eghamat24-mcp",
        "aliases": ["eghamat24", "اقامت۲۴"],
        "keywords": ["اقامت24", "رزرو هتل"],
        "tool": "eg_search",
        "intent_tools": {},
    },
    {
        "id": "neshan-mcp",
        "aliases": ["neshan", "نشان"],
        "keywords": ["نشان", "نقشه", "مسیریاب", "نزدیک من", "map", "directions", "nearby"],
        "tool": "ns_search",
        "intent_tools": {},
    },
    {
        "id": "balad-mcp",
        "aliases": ["balad", "بلد"],
        "keywords": ["بلد", "balad"],
        "tool": "bl_search",
        "intent_tools": {},
    },
    {
        "id": "tsetmc-mcp",
        "aliases": ["tsetmc", "tse"],
        "keywords": [
            "بورس", "سهام", "شاخص بورس", "نماد", "شاخص کل",
            "stock", "tse", "ticker", "shares", "index",
        ],
        "tool": "ts_search_symbols",
        "intent_tools": {"overview": "ts_indices", "history": "ts_price_history"},
    },
    {
        "id": "codal-mcp",
        "aliases": ["codal", "کدال"],
        "keywords": ["کدال", "اطلاعیه شرکت", "codal", "company filing"],
        "tool": "cd_search_letters",
        "intent_tools": {},
    },
    {
        "id": "cbi-mcp",
        "aliases": ["cbi", "بانک مرکزی"],
        "keywords": ["بانک مرکزی", "نرخ رسمی", "central bank"],
        "tool": "cb_exchange_rates",
        "intent_tools": {},
    },
    {
        "id": "paziresh24-mcp",
        "aliases": ["paziresh24", "پذیرش۲۴", "پذیرش24"],
        "keywords": [
            "پذیرش24", "دکتر", "پزشک", "نوبت", "بیمارستان", "درمانگاه",
            "doctor", "clinic", "appointment", "hospital",
        ],
        "tool": "pz_search_doctors",
        "intent_tools": {},
    },
    {
        "id": "snapp-mcp",
        "aliases": ["snappfood", "اسنپ فود", "اسنپفود"],
        "keywords": [
            "اسنپ فود", "غذا", "رستوران", "سفارش غذا", "food", "restaurant",
            "meal", "order food",
        ],
        "tool": "food_search",
        "intent_tools": {"cheapest": "food_find_cheapest"},
    },
    {
        "id": "tapsifood-mcp",
        "aliases": ["tapsifood", "تپسی فود"],
        "keywords": ["تپسی فود", "tapsifood"],
        "tool": "tf_search_dishes",
        "intent_tools": {},
    },
    {
        "id": "jobinja-mcp",
        "aliases": ["jobinja", "جابینجا"],
        "keywords": ["جابینجا", "استخدام", "آگهی شغلی", "job", "hiring"],
        "tool": "jj_search_jobs",
        "intent_tools": {},
    },
    {
        "id": "jobvision-mcp",
        "aliases": ["jobvision", "جابویژن"],
        "keywords": ["جابویژن", "jobvision"],
        "tool": "jv_search",
        "intent_tools": {},
    },
    {
        "id": "irantalent-mcp",
        "aliases": ["irantalent", "ایران تلنت"],
        "keywords": ["ایران تلنت", "حقوق و دستمزد", "salary"],
        "tool": "it_search_jobs",
        "intent_tools": {},
    },
    {
        "id": "quera-mcp",
        "aliases": ["quera", "کوئرا"],
        "keywords": ["کوئرا", "quera"],
        "tool": "qr_jobs",
        "intent_tools": {},
    },
    {
        "id": "ponisha-mcp",
        "aliases": ["ponisha", "پونیشا"],
        "keywords": ["پونیشا", "پروژه فریلنسری", "فریلنسر", "freelance", "ponisha"],
        "tool": "pn_search_projects",
        "intent_tools": {},
    },
    {
        "id": "karlancer-mcp",
        "aliases": ["karlancer", "کارلنسر"],
        "keywords": ["کارلنسر", "karlancer"],
        "tool": "kl_projects",
        "intent_tools": {},
    },
    {
        "id": "varzesh3-mcp",
        "aliases": ["varzesh3", "ورزش۳", "ورزش3"],
        "keywords": [
            "ورزش3", "نتیجه بازی", "فوتبال", "لیگ", "football", "scores",
            "match", "league",
        ],
        "tool": "v3_scores",
        "intent_tools": {},
    },
    {
        "id": "time-ir-mcp",
        "aliases": ["time.ir"],
        "keywords": ["تقویم", "تاریخ امروز", "مناسبت", "تعطیل", "calendar", "date"],
        "tool": "ti_today",
        "intent_tools": {},
    },
    {
        "id": "iran-vod-mcp",
        "aliases": ["filimo", "namava", "فیلیمو", "نماوا"],
        "keywords": [
            "فیلم", "سریال", "قسمت", "فصل", "بازیگر", "کارگردان",
            "کجا ببینم", "تماشا", "movie", "film", "series", "episode",
            "season", "actor", "director", "where to watch", "vod",
        ],
        "tool": "vod_search",
        "intent_tools": {},
    },
    {
        "id": "qavanin-mcp",
        "aliases": ["qavanin", "قوانین"],
        "keywords": ["قوانین", "متن قانون", "قانون", "qavanin", "law"],
        "tool": "qv_search",
        "intent_tools": {},
    },
    {
        "id": "iran-news-mcp",
        "aliases": [],
        "keywords": ["خبر", "اخبار", "news"],
        "tool": "nw_search",
        "intent_tools": {},
    },    {
        "id": "okala-mcp",
        "aliases": ["okala", "اوکالا"],
        "keywords": ["اوکالا", "خرید سوپرمارکتی", "سوپرمارکت آنلاین", "grocery"],
        "tool": "ok_search",
        "intent_tools": {},
    },
    {
        "id": "masterkala-mcp",
        "aliases": ["masterkala", "مسترکالا"],
        "keywords": ["مسترکالا"],
        "tool": "mk_search",
        "intent_tools": {"cheapest": "mk_find_cheapest"},
    },
    {
        "id": "baneh-mcp",
        "aliases": ["baneh", "بانه"],
        "keywords": ["بانه", "خرید از بانه", "لوازم خانگی بانه"],
        "tool": "bn_search",
        "intent_tools": {"cheapest": "bn_find_cheapest"},
    },
    {
        "id": "basalam-mcp",
        "aliases": ["basalam", "باسلام"],
        "keywords": ["باسلام", "بازار باسلام", "غرفه"],
        "tool": "bs_search",
        "intent_tools": {"cheapest": "bs_find_cheapest"},
    },
    {
        "id": "zoomit-mcp",
        "aliases": ["zoomit", "زومیت"],
        "keywords": ["زومیت", "بررسی محصول زومیت"],
        "tool": "zm_search",
        "intent_tools": {},
    },
    {
        "id": "pasavard-mcp",
        "aliases": ["pasavard", "پاساورد"],
        "keywords": ["پاساورد"],
        "tool": "search_products",
        "intent_tools": {},
    },
    {
        "id": "asalbanoo-mcp",
        "aliases": ["asalbanoo", "عسل بانو"],
        "keywords": ["عسل بانو", "لوازم آرایشی", "cosmetics"],
        "tool": "ab_search",
        "intent_tools": {"cheapest": "ab_find_cheapest"},
    },
    {
        "id": "shopino-mcp",
        "aliases": ["shopino", "شاپینو"],
        "keywords": ["شاپینو"],
        "tool": "sh_search",
        "intent_tools": {"cheapest": "sh_find_cheapest"},
    },
    {
        "id": "bama-ir-mcp",
        "aliases": ["bama", "باما"],
        "keywords": ["باما", "آگهی خودرو", "قیمت خودرو", "خرید ماشین", "car ads"],
        "tool": "ba_search",
        "intent_tools": {},
    },
    {
        "id": "karnameh-mcp",
        "aliases": ["karnameh", "کارنامه"],
        "keywords": ["کارنامه", "مشخصات خودرو", "مقایسه خودرو"],
        "tool": "kn_specs_search",
        "intent_tools": {"compare": "kn_compare_specs"},
    },
    {
        "id": "hamrah-mechanic-mcp",
        "aliases": ["hamrah-mechanic", "همراه مکانیک"],
        "keywords": ["همراه مکانیک", "قیمت خودرو کارکرده"],
        "tool": "hm_prices",
        "intent_tools": {},
    },
    {
        "id": "otaghak-mcp",
        "aliases": ["otaghak", "اتاقک"],
        "keywords": ["اتاقک", "اجاره ویلا", "اجاره سوئیت", "villa rental"],
        "tool": "ot_price_quote",
        "intent_tools": {},
    },
    {
        "id": "flytoday-mcp",
        "aliases": ["flytoday", "فلای تودی"],
        "keywords": ["فلای تودی", "بلیط اتوبوس"],
        "tool": "ft_search_buses",
        "intent_tools": {},
    },
    {
        "id": "doctoreto-mcp",
        "aliases": ["doctoreto", "دکترتو"],
        "keywords": ["دکترتو", "نوبت دکتر"],
        "tool": "dt_free_slots",
        "intent_tools": {},
    },
    {
        "id": "exiryab-mcp",
        "aliases": ["exiryab", "اکسیر یاب"],
        "keywords": ["اکسیر یاب"],
        "tool": "ey_search_doctors",
        "intent_tools": {},
    },
    {
        "id": "darukade-mcp",
        "aliases": ["darukade", "داروکده"],
        "keywords": ["داروکده", "دارو", "داروخانه آنلاین", "pharmacy"],
        "tool": "dr_search",
        "intent_tools": {"cheapest": "dr_cheapest"},
    },
    {
        "id": "taaghche-mcp",
        "aliases": ["taaghche", "طاقچه"],
        "keywords": ["طاقچه", "کتاب الکترونیک", "ebook"],
        "tool": "tg_search",
        "intent_tools": {},
    },
    {
        "id": "fidibo-mcp",
        "aliases": ["fidibo", "فیدیبو"],
        "keywords": ["فیدیبو", "کتاب صوتی", "audiobook"],
        "tool": "fd_search",
        "intent_tools": {},
    },
    {
        "id": "30book-mcp",
        "aliases": ["30book", "سی بوک"],
        "keywords": ["سی بوک"],
        "tool": "sb_search",
        "intent_tools": {},
    },
    {
        "id": "iranketab-mcp",
        "aliases": ["iranketab", "ایران کتاب"],
        "keywords": ["ایران کتاب"],
        "tool": "ik_search",
        "intent_tools": {},
    },
    {
        "id": "maktabkhooneh-mcp",
        "aliases": ["maktabkhooneh", "مکتب خونه"],
        "keywords": ["مکتب خونه", "دوره آموزشی", "online course"],
        "tool": "mkh_search",
        "intent_tools": {"cheapest": "mkh_cheapest"},
    },
    {
        "id": "faradars-mcp",
        "aliases": ["faradars", "فرادرس"],
        "keywords": ["فرادرس"],
        "tool": "fr_search_courses",
        "intent_tools": {},
    },
    {
        "id": "iran-apps-mcp",
        "aliases": ["iran-apps"],
        "keywords": ["کافه بازار", "مایکت", "اپلیکیشن اندروید", "android app"],
        "tool": "ap_search",
        "intent_tools": {},
    },
    {
        "id": "iran-downloads-mcp",
        "aliases": ["iran-downloads"],
        "keywords": ["دانلود نرم افزار", "software download"],
        "tool": "dl_search",
        "intent_tools": {},
    },
    {
        "id": "iran-cloud-status-mcp",
        "aliases": ["iran-cloud-status"],
        "keywords": ["وضعیت ابر", "ابر", "ابری", "سرور ابری", "قطعی سرور", "آروان", "cloud status", "outage"],
        "tool": "cs_status",
        "intent_tools": {},
    },
    {
        "id": "iran-crypto-mcp",
        "aliases": ["iran-crypto"],
        "keywords": ["صرافی ارز دیجیتال", "قیمت بیت کوین", "bitcoin price"],
        "tool": "ic_compare_price",
        "intent_tools": {},
    },
    {
        "id": "swapwallet-mcp",
        "aliases": ["swapwallet", "سواپ ولت"],
        "keywords": ["سواپ ولت", "کیف پول"],
        "tool": "get_balance",
        "intent_tools": {},
    },
    {
        "id": "ifb-mcp",
        "aliases": ["ifb", "فرابورس"],
        "keywords": ["فرابورس", "اوراق", "صکوک"],
        "tool": "ifb_search",
        "intent_tools": {},
    },
    {
        "id": "fipiran-mcp",
        "aliases": ["fipiran", "فیپیران"],
        "keywords": ["فیپیران", "صندوق سرمایه گذاری", "mutual fund"],
        "tool": "fp_search_funds",
        "intent_tools": {},
    },
    {
        "id": "ime-mcp",
        "aliases": ["ime", "بورس کالا"],
        "keywords": ["بورس کالا"],
        "tool": "ime_market_summary",
        "intent_tools": {},
    },
    {
        "id": "amar-mcp",
        "aliases": ["amar", "مرکز آمار"],
        "keywords": ["مرکز آمار", "نرخ تورم", "inflation rate", "آمار"],
        "tool": "am_inflation",
        "intent_tools": {},
    },
    {
        "id": "gamefa-mcp",
        "aliases": ["gamefa", "گیمفا"],
        "keywords": ["گیمفا", "اخبار بازی", "game news"],
        "tool": "gf_latest_articles",
        "intent_tools": {},
    },
    {
        "id": "iran-quake-mcp",
        "aliases": ["iran-quake"],
        "keywords": ["زلزله", "earthquake"],
        "tool": "eq_latest",
        "intent_tools": {},
    },
    {
        "id": "rrk-mcp",
        "aliases": ["rrk", "روزنامه رسمی"],
        "keywords": ["روزنامه رسمی", "official gazette"],
        "tool": "rk_search_laws",
        "intent_tools": {},
    },
    {
        "id": "iran-tax-mcp",
        "aliases": ["iran-tax"],
        "keywords": ["مالیات", "ارزش افزوده", "tax"],
        "tool": "tx_faq_search",
        "intent_tools": {},
    },
    {
        "id": "payping-mcp",
        "aliases": ["payping", "پی پینگ"],
        "keywords": ["پی پینگ", "درگاه پرداخت"],
        "tool": "payping_get_balance",
        "intent_tools": {},
    },
    {
        "id": "bale-mcp",
        "aliases": ["bale", "بله"],
        "keywords": ["بله", "ربات بله", "bale bot"],
        "tool": "bot_send_message",
        "intent_tools": {},
    },
]

# Category-level fallback keywords (weight 1). Covers every catalog category.
CATEGORY_KEYWORDS = {
    "prices": ["قیمت ارز", "قیمت طلا", "قیمت سکه", "نرخ", "price"],
    "shopping": ["قیمت", "خرید", "فروشگاه", "تخفیف", "buy", "shop", "discount", "price"],
    "travel": ["سفر", "بلیط", "travel", "ticket", "trip"],
    "stocks": ["بازار سرمایه"],
    "health": ["سلامت", "health"],
    "books": ["کتاب", "book"],
    "jobs": ["شغل", "career"],
    "food": ["خوراکی"],
    "classifieds": ["خرید و فروش"],
    "cars": ["ماشین", "خودرو", "car", "auto"],
    "maps": ["آدرس", "address", "route"],
    "learning": ["آموزش", "دوره", "course", "learn"],
    "freelance": ["دورکاری", "remote"],
    "software": ["اپلیکیشن", "نرم افزار", "app", "software"],
    "economy": ["اقتصاد", "economy"],
    "law": ["حقوقی", "legal"],
    "cloud": ["سرور ابری", "cloud"],
    "news": ["روزنامه"],
    "sports": ["ورزش", "sport"],
    "crypto": ["رمزارز", "کریپتو", "بیت کوین", "crypto", "bitcoin"],
    "beauty": ["آرایشی", "beauty"],
    "fashion": ["لباس", "clothes"],
    "messaging": ["پیام رسان"],
    "business": ["کسب و کار", "business"],
    "entertainment": ["سرگرمی", "entertainment"],
    "calendar": ["اوقات شرعی"],
    "quakes": ["زلزله", "earthquake"],
    "tax": ["مالیات", "tax"],
}

INTENT_WORDS = {
    "cheapest": ["ارزان", "ارزون", "cheapest", "lowest price", "کمترین قیمت", "بهترین قیمت"],
    "history": ["تاریخچه", "نمودار", "history", "chart"],
    "compare": ["مقایسه", "compare", "comparison"],
    "overview": ["خلاصه بازار", "نبض بازار", "market overview", "summary"],
}

_catalog_cache = None


def load_catalog(path=None):
    """Load data/catalog.json (cached)."""
    global _catalog_cache
    if _catalog_cache is None:
        with open(path or CATALOG_PATH, encoding="utf-8") as f:
            _catalog_cache = json.load(f)
    return _catalog_cache


def _hits(query, keywords):
    """Keywords matched as whole words/phrases (word-boundary aware).

    Boundary matching matters in Persian: 'ارز' (currency) must not fire
    inside 'ارزون' (cheap). Python's \\b treats Persian letters as word
    characters, so this works for both scripts.
    """
    out = []
    for k in keywords:
        nk = normalize_fa(k)
        if not nk:
            continue
        pat = _PATTERNS.get(nk)
        if pat is None:
            pat = re.compile(r"\b" + re.escape(nk) + r"\b")
            _PATTERNS[nk] = pat
        if pat.search(query):
            out.append(k)
    return out


def route(query, top_k=3, catalog=None):
    """Route a Persian/English task to iran-mcp servers.

    Returns up to top_k dicts, each with: server_id, title, category,
    suggested_tool, install, repo, score, reason, description.
    Deterministic: ties break by server id.
    """
    nq = normalize_fa(query)
    catalog = catalog or load_catalog()
    by_id = {s["id"]: s for s in catalog["servers"]}

    scored = []
    for rule in SERVER_RULES:
        sid = rule["id"]
        if sid not in by_id:
            continue
        kw_hits = _hits(nq, rule["keywords"])
        alias_hits = _hits(nq, rule["aliases"])
        score = 3 * len(kw_hits) + 4 * len(alias_hits)
        if score == 0:
            continue
        # intent-refined tool choice
        tool = rule["tool"]
        for intent, words in INTENT_WORDS.items():
            if intent in rule.get("intent_tools", {}) and _hits(nq, words):
                tool = rule["intent_tools"][intent]
                break
        srv = by_id[sid]
        reasons = ["کلیدواژه: " + ", ".join(kw_hits)] if kw_hits else []
        if alias_hits:
            reasons.append("نام سرویس: " + ", ".join(alias_hits))
        scored.append((score, sid, tool, reasons))

    # Category fallback: servers with no rule hit but a category keyword hit.
    cat_matched = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        hits = _hits(nq, kws)
        if hits:
            cat_matched[cat] = hits
    if cat_matched:
        ruled_out = {sid for _, sid, _, _ in scored}
        for srv in catalog["servers"]:
            if srv["id"] in ruled_out:
                continue
            hits = cat_matched.get(srv["category"], [])
            if hits:
                tool = srv["tools"][0]["name"] if srv["tools"] else ""
                scored.append(
                    (len(hits), srv["id"], tool, ["دسته‌بندی: " + ", ".join(hits)])
                )

    scored.sort(key=lambda x: (-x[0], x[1]))
    results = []
    for score, sid, tool, reasons in scored[: max(1, top_k)]:
        srv = by_id[sid]
        results.append(
            {
                "server_id": sid,
                "title": srv["title"],
                "category": srv["category"],
                "description": srv["description"],
                "suggested_tool": tool,
                "install": srv["run"],
                "repo": srv["repo"],
                "score": score,
                "reason": "؛ ".join(reasons),
            }
        )
    return results


def main():
    import sys

    query = " ".join(sys.argv[1:]) or "قیمت سکه امامی"
    for r in route(query):
        print(f"[{r['score']}] {r['server_id']} ({r['title']})")
        print(f"  tool: {r['suggested_tool']} | install: {r['install']}")
        print(f"  why: {r['reason']}")


if __name__ == "__main__":
    main()
