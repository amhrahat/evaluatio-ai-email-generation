# Email Generation Assistant

A professional email generation service built with FastAPI, LangGraph, and advanced prompt engineering techniques.

## Quick Start

These instructions show how to run the project locally (development). The app provides a REST API to generate professional emails from three inputs: intent, key facts, and tone. Generated emails are persisted to a local SQLite database.

### Prerequisites

- Python 3.10+
- pip
- Optional: virtual environment tool (venv)

### Install

1. Clone the repository and change directory:

```bash
git clone <repo-url> evaluatio-ai-email-generation
cd evaluatio-ai-email-generation
```

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -e .
# or for development dependencies
pip install -e .[dev]
```

4. Create a copy of the example env and set your LLM key:

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY (or relevant provider key)
```

### Run locally

Start the FastAPI development server using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000. OpenAPI docs are at http://localhost:8000/docs.

## API Usage

Base path: `/api/v1`

1) Generate an email (POST /api/v1/generate-email)

Request body (JSON):

```json
{
   "intent": "Follow up after meeting",
   "key_facts": [
      "Met on June 10",
      "Discussed timeline",
      "Requested budget details"
   ],
   "tone": "formal"
}
```

Example curl:

```bash
curl -sS -X POST http://localhost:8000/api/v1/generate-email \
   -H "Content-Type: application/json" \
   -d '{"intent":"Follow up after meeting","key_facts":["Met on June 10","Discussed timeline","Requested budget details"],"tone":"formal"}'
```

Response (201): JSON with generated email and metadata. Example keys: `id`, `intents`, `key_facts`, `tone`, `subject`, `email`, `created_at`.

2) Retrieve a generated email (GET /api/v1/emails/{email_id})

3) List recent emails (GET /api/v1/emails?skip=0&limit=10)

## Prompting and Design Notes

- Advanced prompt engineering: Few-shot examples + role-playing persona + explicit structured-output instructions to return JSON with `subject` and `body`.
- LangGraph/LLM integration located in `app/core/llm.py`.
- Clean architecture: API routes (`app/api/routes.py`) → services (`app/services`) → core (`app/core/`) → DB (`app/db/`).

## Database

- Uses SQLite by default. Database file: `emails.db` (created in project root unless `DATABASE_URL` in `.env` is changed).
- Single `emails` table with columns: `id`, `intents`, `key_facts` (JSON as text), `tone`, `email` (subject+body), `subject`, `created_at`.

## Tests

Run unit tests with pytest:

```bash
pytest -q
```

## Troubleshooting

- If the LLM API key is missing or invalid, set `OPENAI_API_KEY` (or provider key) in `.env`.
- For production use, replace SQLite with PostgreSQL and secure API access.

## License

MIT
