# evaluatio-ai-email-generation
# Email Generation Assistant

A professional email generation service built with **FastAPI**, **LangGraph**, and **advanced prompt engineering** techniques.

## Features

✨ **Advanced Prompt Engineering**
- Few-Shot Learning: Provides 2-3 realistic examples to guide output quality
- Role-Playing: Adopts "Professional Email Assistant" persona for consistent tone
- Structured Output: Enforces JSON schema for reliable parsing
- Chain-of-Thought: Explicit reasoning instructions for better results

⚙️ **Clean Architecture**
- Layered design: API → Services → Core (LLM) → Database
- Separation of concerns: routes, schemas, models, business logic
- Dependency injection via FastAPI Depends and SQLAlchemy

📊 **Database**
- SQLite with SQLAlchemy ORM
- Single `emails` table with UUID PK
- Fields: id, intents, key_facts (JSON), tone, email (combined), subject, created_at

🔐 **Validation**
- Pydantic V2 for request/response validation
- Intent: 5-500 characters
- Key facts: 1-10 items, non-empty strings
- Tone: one of formal, casual, urgent, empathetic, professional, friendly

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. **Clone the repository**
   ```bash
   cd evaluatio-ai-email-generation