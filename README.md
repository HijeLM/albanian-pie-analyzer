# Albanian PIE Analyzer

Trace Albanian words to their Proto-Indo-European origins. A minimal full-stack app with etymology lookup, cognate discovery, and authenticity scoring.

## Stack

| Layer      | Tech                          |
|------------|-------------------------------|
| Frontend   | React 18 + Vite               |
| Backend    | Python 3.12 + FastAPI         |
| Database   | PostgreSQL 16                 |
| Container  | Docker + Docker Compose       |

---

## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000  
- API docs: http://localhost:8000/docs

The backend automatically seeds 150+ words from the built-in dataset on first run.

---

### Local Development

**Prerequisites:** Python 3.10+, Node 18+, PostgreSQL running

```bash
# 1. Start PostgreSQL and create database
psql -c "CREATE USER pie_user WITH PASSWORD 'pie_pass';"
psql -c "CREATE DATABASE albanian_pie OWNER pie_user;"

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Seed database
python scripts/ingest_orel.py --seed

# Run API
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Or use the convenience script:
```bash
chmod +x dev.sh && ./dev.sh
```

---

## Database Schema

```sql
words        -- word, normalized, language, created_at
sources      -- name, year, author, reliability_weight
entries      -- word_id, source_id, root, meaning, pos, confidence
cognates     -- entry_id, language, word, meaning
evolutions   -- entry_id, stage, form
```

---

## API

### `GET /analyze/{word}`

Analyze an Albanian word.

**Found response:**
```json
{
  "found": true,
  "word": "ujk",
  "meaning": "wolf",
  "type": "noun",
  "root": "*wĺ̥kʷos",
  "cognates": [
    { "language": "Latin", "word": "lupus", "meaning": "wolf" }
  ],
  "evolutions": [
    { "stage": "PIE",   "form": "*wĺ̥kʷos" },
    { "stage": "Albanian", "form": "ujk"  }
  ],
  "sources": ["A Dictionary of Inherited Lexicon"],
  "score": 86.3,
  "label": "Likely",
  "source_count": 1
}
```

**Not found response:**
```json
{
  "found": false,
  "error": true,
  "word": "xyz",
  "score": 17.2,
  "label": "Probably incorrect"
}
```

### `GET /stats`
Returns word, entry, and source counts.

### `GET /health`
Health check.

---

## Authenticity Score

```
score = (agreement_ratio × 0.4 + avg_source_weight × 0.4 + avg_confidence × 0.2) × 100
```

| Score  | Label              |
|--------|--------------------|
| 90–100 | Highly reliable    |
| 70–89  | Likely             |
| 40–69  | Uncertain          |
| < 40   | Probably incorrect |

---

## PDF Ingestion

To parse a real copy of Orel's *Albanian Etymological Dictionary* (1998):

```bash
cd backend
python scripts/ingest_orel.py --pdf /path/to/orel1998.pdf
```

The script:
1. Opens the PDF with `pdfplumber`
2. Applies regex to extract: word, quoted meaning, PIE root (`*...`)
3. Normalizes Albanian characters
4. Inserts into PostgreSQL linked to the Orel source record

To add more sources, create a new `Source` record with its `reliability_weight` and run ingestion pointing to it.

---

## Project Structure

```
albanian-pie/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app + /analyze endpoint
│   │   ├── models.py      # SQLAlchemy ORM models
│   │   ├── database.py    # DB connection + session
│   │   └── scoring.py     # Authenticity score logic
│   ├── scripts/
│   │   └── ingest_orel.py # PDF parser + 150-word seed dataset
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # React app (search + modal)
│   │   └── index.css      # All styles
│   ├── index.html
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
└── dev.sh
```

---

## Dataset

Ships with ~150 Albanian words covering:
- Core vocabulary (body parts, family, numbers, nature)
- High-confidence PIE roots with cognates in Latin, Greek, Sanskrit, English, etc.
- Evolution chains: PIE → Proto-Albanian → Albanian
- Confidence scores per entry

Sources supported: Orel (1998), Mann (1977). Designed to add more.
