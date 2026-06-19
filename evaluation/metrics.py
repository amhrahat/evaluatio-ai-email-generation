import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()


def fact_coverage_score(email: str, key_facts: list[str]) -> float:
    email_lower = email.lower()
    matched = 0

    for fact in key_facts:
        words = fact.lower().split()
        if any(word in email_lower for word in words):
            matched += 1
    
    return matched / len(key_facts) if key_facts else 0.0


def get_judge_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENROUTER_API_KEY must be set for tone scoring")

    return ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model=os.getenv("MODEL", "meta-llama/llama-3.1-8b-instruct"),
        temperature=0.0,
    )


def tone_score(email: str, tone: str) -> float:
    prompt = PromptTemplate(
        input_variables=["tone", "email"],
        template="""
You are a strict evaluator.

Rate how well the email matches the required tone.

Tone required: {tone}

Email:
{email}

Return ONLY a number between 0 and 1.
"""
    )

    try:
        judge_llm = get_judge_llm()
        result = judge_llm.invoke(prompt.format(tone=tone, email=email))
        return float(result.content.strip())
    except Exception:
        email_lower = email.lower()
        tone_keywords = {
            "formal": ["sincerely", "regards", "respectfully", "please", "would"],
            "casual": ["hey", "thanks", "cheers", "awesome", "cool"],
            "urgent": ["urgent", "immediately", "asap", "critical", "deadline"],
            "empathetic": ["understand", "sorry", "appreciate", "support", "care"],
            "professional": ["professional", "regards", "please", "review"],
            "informative": ["note", "details", "information", "update"],
            "appreciative": ["thank", "grateful", "appreciate", "thanks"]
        }
        keywords = tone_keywords.get(tone.lower(), [])
        if not keywords:
            return 0.5
        matched = sum(1 for kw in keywords if kw in email_lower)
        return min(1.0, matched / len(keywords))


def structure_score(email: str) -> float:
    score = 0.0
    text = email.lower()

    if "subject:" in text:
        score += 0.3

    if len(email.split()) < 250:
        score += 0.3

    if "dear" in text or "hello" in text:
        score += 0.2

    if "thank" in text or "regards" in text or "sincerely" in text:
        score += 0.2

    return min(score, 1.0)


def evaluate_email(email: dict, key_facts: list[str], tone: str) -> dict:
    body = email.get("body", "")
    full_email = f"Subject: {email.get('subject', '')}\n\n{body}"

    fcs = fact_coverage_score(full_email, key_facts)
    tcs = tone_score(full_email, tone)
    css = structure_score(full_email)

    return {
        "fact_coverage_score": round(fcs, 4),
        "tone_score": round(tcs, 4),
        "structure_score": round(css, 4),
        "avg": round((fcs + tcs + css) / 3, 4)
    }