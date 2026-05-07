from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
import random
import re

from app.database import get_db, init_db
from app.models import Word, Entry, Cognate, Evolution, Source
from app.scoring import compute_authenticity_score


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    from app.database import SessionLocal
    db = SessionLocal()
    count = db.query(Word).count()
    db.close()
    if count == 0:
        print("Database empty — seeding...")
        import subprocess
        subprocess.run(["python3", "scripts/seed_extended.py"], check=False)
        print("Seeding complete.")
    yield


app = FastAPI(title="Albanian PIE Analyzer", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_word(word: str) -> str:
    """Normalize Albanian word: lowercase, strip accents from non-Albanian chars."""
    return word.strip().lower()


@app.get("/analyze/{word}")
def analyze_word(word: str, db: Session = Depends(get_db)):
    normalized = normalize_word(word)

    # Find word record
    word_record = (
        db.query(Word)
        .filter((Word.word == normalized) | (Word.normalized == normalized))
        .first()
    )

    if not word_record:
        score = round(random.uniform(10, 30), 1)
        return {
            "found": False,
            "word": word,
            "error": True,
            "score": score,
            "label": "Probably incorrect",
            "message": f"Word '{word}' not found in any source.",
        }

    # Load entries with related data
    entries = (
        db.query(Entry)
        .options(
            joinedload(Entry.source),
            joinedload(Entry.cognates),
            joinedload(Entry.evolutions),
        )
        .filter(Entry.word_id == word_record.id)
        .all()
    )

    if not entries:
        return {
            "found": False,
            "word": word,
            "error": True,
            "score": 15,
            "label": "Probably incorrect",
            "message": f"No entries found for '{word}'.",
        }

    # Pick best entry (highest confidence, or first)
    best_entry = max(entries, key=lambda e: e.confidence or 0)

    # Aggregate cognates across all entries
    all_cognates = []
    seen = set()
    for entry in entries:
        for cog in entry.cognates:
            key = (cog.language, cog.word)
            if key not in seen:
                seen.add(key)
                all_cognates.append({
                    "language": cog.language,
                    "word": cog.word,
                    "meaning": cog.meaning,
                })

    # Aggregate evolutions from best entry
    evolutions = [
        {"stage": ev.stage, "form": ev.form}
        for ev in sorted(best_entry.evolutions, key=lambda e: _stage_order(e.stage))
    ]

    # Sources used
    sources = list({e.source.name for e in entries if e.source})

    # Authenticity score
    auth = compute_authenticity_score(entries)

    return {
        "found": True,
        "word": word_record.word,
        "meaning": best_entry.meaning,
        "type": best_entry.part_of_speech or "unknown",
        "root": best_entry.root,
        "notes": best_entry.notes,
        "cognates": all_cognates,
        "evolutions": evolutions,
        "sources": sources,
        "score": auth["score"],
        "label": auth["label"],
        "source_count": auth["source_count"],
    }


def _stage_order(stage: str) -> int:
    order = {"PIE": 0, "Proto-Albanian": 1, "Old Albanian": 2, "Albanian": 3}
    return order.get(stage, 99)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    word_count = db.query(Word).count()
    entry_count = db.query(Entry).count()
    source_count = db.query(Source).count()
    return {
        "words": word_count,
        "entries": entry_count,
        "sources": source_count,
    }


@app.get("/search")
def search_words(q: str = "", limit: int = 8, db: Session = Depends(get_db)):
    if not q.strip():
        return []
    normalized = q.strip().lower()
    words = (
        db.query(Word)
        .join(Entry)
        .options(joinedload(Word.entries))
        .filter(Word.normalized.startswith(normalized))
        .order_by(Word.word)
        .limit(limit)
        .all()
    )
    return [
        {
            "word": w.word,
            "meaning": w.entries[0].meaning if w.entries else None,
        }
        for w in words
    ]


@app.get("/sources")
def get_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).order_by(Source.year).all()
    return [
        {"id": s.id, "name": s.name, "year": s.year, "author": s.author}
        for s in sources
    ]


@app.get("/words")
def get_words(
    db: Session = Depends(get_db),
    limit: int = 500,
    offset: int = 0,
    source_id: int = None,
):
    q = db.query(Word).join(Entry).options(joinedload(Word.entries))
    if source_id:
        q = q.filter(Entry.source_id == source_id)
    words = q.order_by(Word.word).offset(offset).limit(limit).all()
    return [
        {
            "word": w.word,
            "meaning": w.entries[0].meaning if w.entries else None,
            "root": w.entries[0].root if w.entries else None,
        }
        for w in words
    ]


