"""
Parse Orel (1998) Albanian Etymological Dictionary PDF and seed the database.
Usage: python scripts/parse_orel.py
Idempotent: skips words already in DB.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pdfplumber
from app.database import SessionLocal, init_db
from app.models import Word, Entry, Cognate, Evolution, Source

PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Albanian etymological dictionary (Vladimir Orel) (z-library.sk, 1lib.sk, z-lib.sk).pdf")

# Pages with actual dictionary entries (0-indexed); skip intro/preface
DICT_START = 21
DICT_END   = 285   # last real entry page

# Language abbreviation → full name
LANG_MAP = {
    "Gk": "Greek", "Lat": "Latin", "Skt": "Sanskrit", "ON": "Old Norse",
    "OE": "Old English", "OHG": "Old High German", "Goth": "Gothic",
    "Lith": "Lithuanian", "Latv": "Latvian", "OIr": "Old Irish",
    "W": "Welsh", "Arm": "Armenian", "Av": "Avestan",
    "Russ": "Russian", "Slav": "Slavic", "Bulg": "Bulgarian",
    "OCS": "Old Church Slavic", "Rum": "Rumanian", "OPrus": "Old Prussian",
    "OBret": "Old Breton", "MW": "Middle Welsh", "MHG": "Middle High German",
    "Gaul": "Gaulish", "Alb": "Albanian", "SCr": "Serbo-Croatian",
    "CS": "Church Slavic", "NPers": "New Persian", "OPers": "Old Persian",
    "Tokh": "Tokharian", "Phryg": "Phrygian", "Thr": "Thracian",
    "Illyr": "Illyrian", "Hitt": "Hittite", "Dac": "Dacian",
    "Georg": "Georgian", "Hung": "Hungarian", "Turk": "Turkish",
    "Fr": "French", "Sp": "Spanish", "It": "Italian", "Pol": "Polish",
    "Ukr": "Ukrainian", "Norw": "Norwegian", "Swed": "Swedish",
    "Rom": "Romance", "Celt": "Celtic", "Balt": "Baltic",
    "Gmc": "Germanic", "IE": "Proto-Indo-European",
}

# Part of speech markers from Orel entries
POS_MARKERS = {
    r'\bm\b': 'noun', r'\bf\b': 'noun', r'\bn\b': 'noun',
    r'\badj\b': 'adjective', r'\badv\b': 'adverb',
    r'\bconj\b': 'conjunction', r'\bpart\b': 'particle',
    r'\bpron\b': 'pronoun', r'\bprep\b': 'preposition',
    r'\bnum\b': 'numeral', r'\baor\b': 'verb', r'\bvb\b': 'verb',
}


def extract_text_from_pdf(path):
    """Extract all text from dictionary pages, column-aware."""
    all_text = []
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        print(f"PDF has {total} pages. Parsing pages {DICT_START+1}–{DICT_END+1}...")
        for page_num in range(DICT_START, min(DICT_END + 1, total)):
            page = pdf.pages[page_num]
            # Try to split into two columns by x midpoint
            width = page.width
            mid = width / 2
            left  = page.crop((0, 0, mid, page.height)).extract_text() or ""
            right = page.crop((mid, 0, width, page.height)).extract_text() or ""
            # Append both columns separately
            all_text.append(left)
            all_text.append(right)
            if (page_num - DICT_START) % 20 == 0:
                print(f"  ...page {page_num + 1}")
    return "\n".join(all_text)


def clean_text(text):
    """Normalize OCR artifacts."""
    # Fix common OCR errors in this PDF
    text = text.replace("PAIb", "PAlb")   # OCR: capital I → l
    text = text.replace("PAlb.", "PAlb")
    text = text.replace("ä", "ä").replace("ö", "ö")
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text


def split_entries(text):
    """
    Split text into individual dictionary entries.
    Each entry starts with a lowercase Albanian headword (or Geg marker).
    Pattern: word at line start, followed by pos marker or pl. or meaning.
    """
    # Entry boundary: a line that starts with a lowercase word (Albanian headword)
    # followed by common entry markers
    # Strict: headword is a single lowercase Albanian word (2-25 chars, no spaces)
    # followed immediately by a grammar marker
    entry_start = re.compile(
        r'(?:^|\n)'
        r'(?:\(G\)\s*)?'
        r'([a-z\xeb\xe7][a-z\xeb\xe7\xe0\xe1\xe2\xe3\xe8\xe9\xea\xec\xed\xee\xef\xf2\xf3\xf4\xf5\xf9\xfa\xfb\xfc\xfd\xff]{1,24})'
        r'(?:\s+[a-z\xeb\xe7][a-z\xeb\xe7]{1,20})?'   # optional alternate form
        r'(?=\s+(?:m\b|f\b|n\b|adj\b|adv\b|conj\b|pron\b|part\b|num\b|aor\.|pl\.|vb\.|\'|\())',
        re.MULTILINE
    )

    entries = []
    matches = list(entry_start.finditer(text))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        entry_text = text[start:end].strip()
        headword = m.group(1).strip()  # always just the first word
        entries.append((headword, entry_text))
    return entries


def extract_meaning(entry_text):
    """Extract first meaning from single-quoted strings."""
    meanings = re.findall(r"'([^']{2,80})'", entry_text)
    if meanings:
        # Skip meanings that look like bibliographic references
        for m in meanings:
            if not re.search(r'\d{3,}|MEYER|JOKL|cABEJ|PEDERSEN', m):
                return m.strip()
    return None


def extract_pos(entry_text):
    """Extract part of speech."""
    # Look at first 120 chars
    head = entry_text[:120]
    for pattern, pos in POS_MARKERS.items():
        if re.search(pattern, head):
            return pos
    return "noun"  # default


def extract_pie_root(entry_text):
    """Extract PIE root (*xxx-) from entry text."""
    # Look for IE *xxx patterns
    patterns = [
        r'IE\s+\*([A-Za-zāḗḱǵħŋšžθðñ₁₂₃ʰʷ̥̄̈\-₀⁰éáōū₄h̯ʔɣɸ()]+)',
        r'(?:from|continuing|represents|reflects|goes back to)\s+PAlb\s+\*\S+\s+[a-z]+\s+IE\s+\*([A-Za-z₁₂₃ʰʷ\-()áéōū̥]+)',
    ]
    for pat in patterns:
        m = re.search(pat, entry_text)
        if m:
            root = m.group(1).strip().rstrip('.,;')
            if 1 < len(root) < 25:
                return '*' + root
    return None


def extract_palb(entry_text):
    """Extract Proto-Albanian reconstruction."""
    m = re.search(r'PAlb\s+\*([A-Za-zëçënjgjllrrshshzhxhthàáâãèéêëìíîïòóôõùúûü\-]+)', entry_text)
    if m:
        form = m.group(1).strip().rstrip('.,;')
        if 1 < len(form) < 30:
            return '*' + form
    return None


def extract_cognates(entry_text):
    """
    Extract cognates: language abbreviation + word + optional meaning.
    Looks for patterns like: Lat aqua 'water', Gk ύδωρ 'water'
    """
    cognates = []
    seen = set()

    # Pattern: LANG word 'meaning'
    pattern = re.compile(
        r'\b(' + '|'.join(re.escape(k) for k in sorted(LANG_MAP.keys(), key=len, reverse=True)) + r')\b'
        r'\s+'
        r'([A-Za-z*āḗḱǵħŋšžθðñ₁₂₃ʰʷ̥̄̈éáōūëçàâãèêìíîïòóôõùúûüýÿ\-]+)'
        r'(?:\s+\'([^\']{1,60})\')?' ,
        re.UNICODE
    )

    # Only search the first ~600 chars of each entry (main etymology section)
    # Skip the reference section (after '0 MEYER...' or '0 CAMARDA...')
    ref_match = re.search(r'\.\s+0\s+[A-Z]{2,}', entry_text)
    search_text = entry_text[:ref_match.start()] if ref_match else entry_text[:800]

    for m in pattern.finditer(search_text):
        lang_abbr = m.group(1)
        word      = m.group(2).strip()
        meaning   = m.group(3).strip() if m.group(3) else None
        lang_full = LANG_MAP.get(lang_abbr, lang_abbr)

        # Skip Albanian self-references and single-char words
        if lang_abbr == "Alb" or len(word) < 2:
            continue
        # Skip words that look like reconstructions or references
        if word.startswith('*') or word[0].isupper():
            continue

        key = (lang_full, word)
        if key not in seen:
            seen.add(key)
            cognates.append({"language": lang_full, "word": word, "meaning": meaning})

    return cognates[:10]  # cap at 10 per entry


_ENGLISH_STOPWORDS = {
    "the", "a", "an", "in", "of", "to", "is", "it", "as", "at", "be",
    "by", "do", "go", "he", "if", "me", "my", "no", "on", "or", "so",
    "up", "us", "we", "word", "form", "from", "with", "that", "this",
    "are", "was", "has", "had", "not", "but", "for", "and", "its",
    "also", "than", "then", "thus", "when", "with", "which", "where",
    "while", "same", "some", "such", "have", "been", "into",
}

def is_valid_albanian_word(word):
    """Basic validation that the word looks like Albanian."""
    if not word:
        return False
    if len(word) < 2 or len(word) > 30:
        return False
    if word.lower() in _ENGLISH_STOPWORDS:
        return False
    # Must contain at least one vowel
    if not re.search(r'[aeiou\xebya\xe0\xe1\xe2\xe3\xe8\xe9\xea\xec\xed\xee\xef\xf2\xf3\xf4\xf5\xf9\xfa\xfb\xfc]', word, re.I):
        return False
    # Reject page headers, numbers, abbreviations
    if re.match(r'^\d+$', word):
        return False
    if word.isupper():
        return False
    # Must start with lowercase
    if word[0].isupper():
        return False
    return True


def compute_confidence(entry_text, pie_root, cognates):
    """Heuristic confidence score."""
    score = 0.5
    if pie_root:
        score += 0.2
    if cognates:
        score += min(0.1 * len(cognates), 0.25)
    if 'PAlb' in entry_text:
        score += 0.05
    if 'borrowed' in entry_text.lower() or 'loanword' in entry_text.lower():
        score -= 0.15
    return round(min(max(score, 0.3), 0.97), 2)


def build_evolutions(word, palb_form, pie_root):
    """Build a simple evolution chain."""
    chain = []
    if pie_root:
        chain.append({"stage": "PIE", "form": pie_root})
    if palb_form:
        chain.append({"stage": "Proto-Albanian", "form": palb_form})
    if word:
        chain.append({"stage": "Albanian", "form": word})
    return chain


def seed_entries(entries, db, source):
    added = 0
    skipped = 0
    bad = 0

    for word_str, entry_text in entries:
        word_str = word_str.strip().lower()

        if not is_valid_albanian_word(word_str):
            bad += 1
            continue

        # Skip already-seeded
        existing = db.query(Word).filter_by(word=word_str).first()
        if existing:
            skipped += 1
            continue

        meaning = extract_meaning(entry_text)
        if not meaning:
            bad += 1
            continue

        pos      = extract_pos(entry_text)
        pie_root = extract_pie_root(entry_text)
        palb     = extract_palb(entry_text)
        cognates = extract_cognates(entry_text)
        conf     = compute_confidence(entry_text, pie_root, cognates)
        evos     = build_evolutions(word_str, palb, pie_root)

        # Detect loanword notes
        notes = None
        if re.search(r'borrowed from|loanword from', entry_text, re.I):
            m = re.search(r'(borrowed from [^.]{5,60}|loanword from [^.]{5,60})', entry_text, re.I)
            if m:
                notes = m.group(1).strip()

        try:
            word_obj = Word(word=word_str, normalized=word_str)
            db.add(word_obj)
            db.flush()

            entry_obj = Entry(
                word_id=word_obj.id,
                source_id=source.id,
                meaning=meaning,
                part_of_speech=pos,
                root=pie_root,
                confidence=conf,
                notes=notes,
            )
            db.add(entry_obj)
            db.flush()

            for evo in evos:
                db.add(Evolution(entry_id=entry_obj.id, stage=evo["stage"], form=evo["form"]))

            for cog in cognates:
                db.add(Cognate(
                    entry_id=entry_obj.id,
                    language=cog["language"],
                    word=cog["word"],
                    meaning=cog["meaning"],
                ))

            added += 1

            if added % 100 == 0:
                db.commit()
                print(f"  Committed {added} entries so far...")

        except Exception as e:
            db.rollback()
            print(f"  Error on '{word_str}': {e}")
            bad += 1

    db.commit()
    return added, skipped, bad


def main():
    init_db()
    db = SessionLocal()

    try:
        source = db.query(Source).filter_by(name="Orel (1998)").first()
        if not source:
            source = Source(
                name="Orel (1998)",
                year=1998,
                author="Vladimir Orel",
                reliability_weight=0.95,
            )
            db.add(source)
            db.commit()

        print("Extracting text from PDF...")
        raw = extract_text_from_pdf(PDF_PATH)
        print(f"Extracted {len(raw):,} characters.")

        print("Cleaning text...")
        text = clean_text(raw)

        print("Splitting into entries...")
        entries = split_entries(text)
        print(f"Found {len(entries)} candidate entries.")

        print("Seeding database...")
        added, skipped, bad = seed_entries(entries, db, source)

        print(f"\nDone: {added} added, {skipped} skipped (already existed), {bad} invalid/skipped.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
