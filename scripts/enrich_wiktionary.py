"""
Wiktionary enrichment script.
For each Albanian word in the DB, fetches its Wiktionary page and extracts:
  - additional meanings
  - PIE roots
  - cognates from template tags
  - Proto-Albanian forms

Adds a "Wiktionary" source and creates new Entry rows (without replacing Orel data).
Rate-limited to 1 request/second to be polite.

Usage: python scripts/enrich_wiktionary.py
"""
import sys, os, re, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request
import urllib.parse

from app.database import SessionLocal, init_db
from app.models import Word, Entry, Cognate, Evolution, Source

init_db()

WIKTIONARY_API = "https://en.wiktionary.org/w/api.php"
REQUEST_DELAY  = 0.5   # seconds between requests (Wiktionary allows ~200 req/min)

# Wiktionary language code → full name
WIKT_LANG = {
    "la": "Latin", "grc": "Greek", "sa": "Sanskrit", "got": "Gothic",
    "ang": "Old English", "goh": "Old High German", "non": "Old Norse",
    "lt": "Lithuanian", "lv": "Latvian", "ga": "Old Irish", "cy": "Welsh",
    "hy": "Armenian", "ae": "Avestan", "ru": "Russian", "pl": "Polish",
    "bg": "Bulgarian", "mk": "Macedonian", "ro": "Rumanian", "de": "German",
    "fr": "French", "es": "Spanish", "it": "Italian", "en": "English",
    "sq": "Albanian", "ine-pro": "Proto-Indo-European",
    "sqj-pro": "Proto-Albanian", "sla-pro": "Proto-Slavic",
    "gem-pro": "Proto-Germanic", "cel-pro": "Proto-Celtic",
    "grk-pro": "Proto-Greek", "ira-pro": "Proto-Iranian",
    "bat-pro": "Proto-Baltic",
}


def fetch_wikitext(word):
    """Fetch raw wikitext for a word from English Wiktionary."""
    params = urllib.parse.urlencode({
        "action": "parse",
        "page": word,
        "prop": "wikitext",
        "formatversion": "2",
        "format": "json",
    })
    url = f"{WIKTIONARY_API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "AlbanianPIEAnalyzer/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data.get("parse", {}).get("wikitext", "")
    except Exception:
        return ""


def extract_albanian_section(wikitext):
    """Extract only the ==Albanian== section from wikitext."""
    # Find ==Albanian== header
    m = re.search(r'==Albanian==\n(.*?)(?=\n==[^=]|\Z)', wikitext, re.DOTALL)
    return m.group(1) if m else ""


def parse_etymology(section):
    """
    Parse etymology from Albanian wikitext section.
    Returns: (pie_root, palb_form, cognates_list, meaning)
    """
    pie_root  = None
    palb_form = None
    cognates  = []
    meaning   = None

    # Extract Etymology sub-section
    etym_m = re.search(r'===Etymology[^=]*===\n(.*?)(?=\n===|\Z)', section, re.DOTALL)
    etym = etym_m.group(1) if etym_m else section

    # PIE root: {{der|sq|ine-pro|*xxx}} or {{inh|sq|ine-pro|*xxx}}
    for m in re.finditer(r'\{\{(?:der|inh|bor)\|sq\|([a-z\-]+)\|(\*[^\|}\s]{1,30})', etym):
        lang_code = m.group(1)
        form      = m.group(2).strip().rstrip("|}")
        lang_name = WIKT_LANG.get(lang_code, lang_code)

        if lang_code == "ine-pro":
            pie_root = form
        elif lang_code == "sqj-pro":
            palb_form = form
        elif lang_code != "sq" and len(form) > 1:
            cognates.append({"language": lang_name, "word": form, "meaning": None})

    # Cognates from {{cog|LANG|word|meaning}} or {{l|LANG|word}}
    for m in re.finditer(r'\{\{(?:cog|l|m)\|([a-z\-]+)\|(\*?[^\|}{]{1,30})(?:\|([^\|}{]{1,60}))?\}\}', etym):
        lang_code = m.group(1)
        word_form = m.group(2).strip()
        gloss     = m.group(3).strip() if m.group(3) else None
        lang_name = WIKT_LANG.get(lang_code, None)
        if lang_name and lang_name != "Albanian" and len(word_form) > 1:
            cognates.append({"language": lang_name, "word": word_form, "meaning": gloss})

    # Meaning: first # line in Noun/Verb/Adjective section
    meaning_m = re.search(r'\n# ([^\n\[{]{3,80})', section)
    if meaning_m:
        raw = meaning_m.group(1).strip()
        # Strip wiki markup
        raw = re.sub(r'\[\[([^\]|]+\|)?([^\]]+)\]\]', r'\2', raw)
        raw = re.sub(r'\{\{[^}]+\}\}', '', raw)
        raw = re.sub(r"'{2,}", '', raw)
        raw = raw.strip().rstrip('.')
        if 2 < len(raw) < 120:
            meaning = raw

    # Deduplicate cognates
    seen = set()
    unique = []
    for c in cognates:
        k = (c["language"], c["word"])
        if k not in seen:
            seen.add(k)
            unique.append(c)

    return pie_root, palb_form, unique[:8], meaning


def build_evolutions(word_str, palb_form, pie_root):
    chain = []
    if pie_root:
        chain.append({"stage": "PIE", "form": pie_root})
    if palb_form:
        chain.append({"stage": "Proto-Albanian", "form": palb_form})
    chain.append({"stage": "Albanian", "form": word_str})
    return chain


def main():
    db = SessionLocal()
    try:
        # Get or create Wiktionary source
        source = db.query(Source).filter_by(name="Wiktionary").first()
        if not source:
            source = Source(
                name="Wiktionary",
                year=2024,
                author="Wiktionary contributors",
                reliability_weight=0.75,
            )
            db.add(source)
            db.commit()

        # Get all words in DB
        words = db.query(Word).order_by(Word.word).all()
        total = len(words)
        print(f"Enriching {total} words from Wiktionary...")
        print("(This will take a while — 1 request/second)\n")

        enriched = 0
        not_found = 0
        skipped   = 0

        for idx, word_obj in enumerate(words):
            word_str = word_obj.word

            # Skip if Wiktionary entry already exists
            already = db.query(Entry).filter_by(
                word_id=word_obj.id, source_id=source.id
            ).first()
            if already:
                skipped += 1
                continue

            wikitext = fetch_wikitext(word_str)
            time.sleep(REQUEST_DELAY)

            if not wikitext:
                not_found += 1
                continue

            alb_section = extract_albanian_section(wikitext)
            if not alb_section:
                not_found += 1
                continue

            pie_root, palb_form, cognates, meaning = parse_etymology(alb_section)

            # Need at least a meaning or PIE root to be worth adding
            if not meaning and not pie_root and not cognates:
                not_found += 1
                continue

            # Fall back to existing meaning if Wiktionary has none
            if not meaning:
                existing = db.query(Entry).filter_by(word_id=word_obj.id).first()
                if existing:
                    meaning = existing.meaning

            if not meaning:
                not_found += 1
                continue

            # Get existing root if Wiktionary has none
            if not pie_root:
                existing = db.query(Entry).filter_by(word_id=word_obj.id).first()
                if existing and existing.root:
                    pie_root = existing.root

            entry = Entry(
                word_id=word_obj.id,
                source_id=source.id,
                meaning=meaning,
                part_of_speech=None,
                root=pie_root,
                confidence=0.80,
            )
            db.add(entry)
            db.flush()

            for evo in build_evolutions(word_str, palb_form, pie_root):
                db.add(Evolution(entry_id=entry.id, stage=evo["stage"], form=evo["form"]))

            for cog in cognates:
                db.add(Cognate(
                    entry_id=entry.id,
                    language=cog["language"],
                    word=cog["word"],
                    meaning=cog["meaning"],
                ))

            enriched += 1

            if enriched % 10 == 0:
                db.commit()
                pct = round((idx + 1) / total * 100)
                print(f"  [{pct}%] {enriched} enriched, {not_found} not on Wiktionary...")

        db.commit()
        print(f"\nDone!")
        print(f"  Enriched: {enriched} words got Wiktionary data")
        print(f"  Not found: {not_found} words not on Wiktionary")
        print(f"  Skipped: {skipped} already had Wiktionary entries")

    finally:
        db.close()


if __name__ == "__main__":
    main()
