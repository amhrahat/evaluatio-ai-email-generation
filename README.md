# Email Generation Assistant

A professional email generation service built with FastAPI, LangGraph, and advanced prompt engineering techniques. Includes a comprehensive evaluation framework for measuring email quality across multiple dimensions.

## Project Structure

```
evaluatio-ai-email-generation/
├── app/
│   ├── api/
│   │   └── routes.py          # FastAPI route definitions
│   ├── core/
│   │   └── llm.py             # LLM integration and email generation
│   │   └── llm2.py            # LLM2 integration and email generation
│   ├── db/
│   │   ├── models.py          # SQLAlchemy database models
│   │   └── session.py         # Database session management
│   ├── services/
│   │   └── email_service.py   # Business logic for email operations
│   ├── main.py                # FastAPI application entry point
│   └── schemas.py             # Pydantic schemas for request/response
├── evaluation/
│   ├── runner.py              # Evaluation test runner
│   ├── metrics.py             # Evaluation metrics implementation
│   ├── test_cases.json        # Test case definitions
│   ├── evaluation_report1.csv  # CSV evaluation results
│   └── evaluation_report1.json # JSON evaluation results
│   ├── evaluation_report2.csv  # CSV evaluation results
│   └── evaluation_report2.json # JSON evaluation results
├── pyproject.toml             # Project dependencies (uv)
├── uv.lock                    # Locked dependency versions
├── .env                       # Environment variables (create from .env.example)
└── README.md                  # This file
```

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain & LangGraph**: LLM orchestration and agent workflows
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **uv**: Fast Python package installer and resolver
- **SQLite**: Lightweight database (configurable to PostgreSQL)

## Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer

### Installation

1. Clone the repository:

```bash
git clone <repo-url> evaluatio-ai-email-generation
cd evaluatio-ai-email-generation
```

2. Create and activate a virtual environment using uv:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv sync
```

4. Configure environment variables:

```bash
cp env.example .env
# Edit .env and set your API keys:
# - OPENAI_API_KEY (for email generation)
# - OPENROUTER_API_KEY (for evaluation tone scoring)
# - MODEL (optional, defaults to meta-llama/llama-3.1-8b-instruct)
```

## Running the Application

### FastAPI Server

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

### Evaluation Runner

Run the evaluation suite to test email generation quality:

```bash
python evaluation/runner.py
```

This will:
- Load test cases from `evaluation/test_cases.json`
- Generate emails for each test case
- Evaluate generated emails against metrics
- Save results to `evaluation/evaluation_report.csv` and `.json`

## API Usage

Base path: `/api/v1`

### Generate Email

**POST** `/api/v1/generate-email`

Request body:

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
curl -X POST http://localhost:8000/api/v1/generate-email \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Follow up after meeting",
    "key_facts": ["Met on June 10", "Discussed timeline", "Requested budget details"],
    "tone": "formal"
  }'
```

Response (201):

```json
{
  "id": "uuid",
  "intents": "Follow up after meeting",
  "key_facts": ["Met on June 10", "Discussed timeline", "Requested budget details"],
  "tone": "formal",
  "subject": "Follow-up: Our Meeting on June 10",
  "email": "Subject: Follow-up: Our Meeting on June 10\n\nDear [Name],\n\n...",
  "created_at": "2026-06-19T10:00:00Z"
}
```

### Retrieve Email

**GET** `/api/v1/emails/{email_id}`

### List Emails

**GET** `/api/v1/emails?skip=0&limit=10`

## Evaluation Framework

The evaluation framework measures email quality across three key metrics:

### Metrics

1. **Fact Coverage Score** (`fact_coverage`)
   - Measures how many required key facts are present in the generated email
   - Calculated as: `matched_facts / total_facts`
   - Range: 0.0 to 1.0

2. **Tone Score** (`tone_score`)
   - Evaluates how well the email matches the requested tone
   - Uses an LLM judge (OpenRouter) when available
   - Falls back to keyword matching if LLM unavailable
   - Range: 0.0 to 1.0

3. **Structure Score** (`structure_score`)
   - Assesses email structure quality
   - Checks for: subject line, appropriate length, greeting, closing
   - Range: 0.0 to 1.0

### Average Score

The overall quality is calculated as the average of all three metrics:

```
avg = (fact_coverage + tone_score + structure_score) / 3
```

### Test Cases

Test cases are defined in `evaluation/test_cases.json` with the following structure:

```json
{
  "id": 1,
  "intent": "Follow up after interview",
  "key_facts": ["Interview was on Monday", "Position: Backend Engineer"],
  "tone": "formal",
  "reference_email": "..."
}
```

### Evaluation Reports

After running the evaluation, two reports are generated:

- **CSV Report** (`evaluation_report1.csv`): Tab-separated with metric definitions
- **JSON Report** (`evaluation_report1.json`): Structured data for programmatic analysis

## Model Comparison Strategy

The evaluation framework is designed to compare two different LLM strategies under identical test conditions.

### Models Used

- **Model 1 (High-performance baseline)**  
  GPT-4o-mini with advanced prompt engineering (role-based + structured instructions + few-shot guidance)

- **Model 2 (Lower-capability comparison model)**  
  meta-llama/llama-3.2-1b-instruct with the same evaluation pipeline

### Prompting Strategy Comparison

Each model is evaluated under two different prompting approaches:

- Advanced structured prompt (role + constraints + explicit reasoning flow)
- Minimal baseline prompt (simple instruction-only format)

### Evaluation Execution

Both models are executed using the same 10 test scenarios in a single evaluation run.

For each model:
- Emails are generated for all test cases
- Custom metrics are computed (Fact Coverage, Tone Score, Structure Score)
- Results are exported independently

### Output Artifacts

The evaluation script generates separate output files:

- `evaluation_report1.csv`
- `evaluation_report2.csv`

These files are used for comparative analysis and final reporting.
## Database

- **Default**: SQLite (`emails.db` in project root)
- **Configurable**: Set `DATABASE_URL` in `.env` to use PostgreSQL
- **Schema**: Single `emails` table with columns for id, intents, key_facts, tone, email, subject, and created_at



### Code Style

The project follows standard Python conventions with type hints and docstrings.

## Troubleshooting

- **Missing API Key**: Ensure `OPENAI_API_KEY` is set in `.env` for email generation
- **Tone Scoring Fails**: Set `OPENROUTER_API_KEY` in `.env` for LLM-based tone evaluation
- **Database Errors**: Check `DATABASE_URL` in `.env` and ensure database file is writable
- **Import Errors**: Ensure virtual environment is activated and dependencies are installed with `uv sync`

