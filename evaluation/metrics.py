import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()


# Fact Coverage Score
_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "by", "for", "with", "about", "as",
    "and", "or", "but", "if", "this", "that", "these", "those", "it",
    "will", "would", "can", "could", "should", "we", "our", "i", "you",
    "your", "from", "into", "than", "then",
}


def _significant_words(text: str) -> list[str]:
    """Lower-cased alphanumeric tokens, with common stopwords removed."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS]


def fact_coverage_score(email: str, key_facts: list[str]) -> float:
    """
    Per-fact partial credit: for each key fact, the fraction of its
    significant (non-stopword) words that appear in the email, matched on
    word boundaries. The final score is the mean across all facts.

    Replaces the old "any single overlapping word = fully covered" logic,
    which gave a fact like "Position: Backend Engineer" full credit if the
    word "Position" showed up anywhere -- even if "Backend Engineer" never
    appeared. Multi-word facts now have to be substantially present, and
    partial inclusion is rewarded proportionally instead of all-or-nothing.
    """
    if not key_facts:
        return 0.0

    email_lower = email.lower()
    per_fact_scores = []

    for fact in key_facts:
        sig_words = _significant_words(fact)
        if not sig_words:
            continue
        matched = sum(
            1 for w in sig_words
            if re.search(rf"\b{re.escape(w)}\b", email_lower)
        )
        per_fact_scores.append(matched / len(sig_words))

    return sum(per_fact_scores) / len(per_fact_scores) if per_fact_scores else 0.0




def get_judge_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENROUTER_API_KEY must be set for tone scoring")

    return ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model=os.getenv("MODEL"),
        temperature=0.0,
    )


_TONE_PROMPT = PromptTemplate(
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

# Matches "0.8", ".8", "1", "85" etc. -- whichever number the judge writes first.
_NUMBER_RE = re.compile(r"\d*\.\d+|\d+")


def _extract_score(raw: str) -> float | None:
    """Pull the first number out of the judge's reply and clamp to [0, 1].
    Returns None (rather than letting float() raise) so a malformed judge
    reply is an explicit, loggable failure instead of silently looking
    identical to "no judge available"."""
    match = _NUMBER_RE.search(raw)
    if not match:
        return None
    return max(0.0, min(1.0, float(match.group())))


def _keyword_tone_fallback(email_lower: str, tone: str) -> float:
    tone_keywords = {
        "formal": ["sincerely", "regards", "respectfully", "please", "would"],
        "casual": ["hey", "thanks", "cheers", "awesome", "cool"],
        "urgent": ["urgent", "immediately", "asap", "critical", "deadline"],
        "empathetic": ["understand", "sorry", "appreciate", "support", "care"],
        "professional": ["professional", "regards", "please", "review"],
        "informative": ["note", "details", "information", "update"],
        "appreciative": ["thank", "grateful", "appreciate", "thanks"],
        # added so unseen tones don't default to a flat, non-discriminating 0.5
        "exciting": ["excited", "thrilled", "amazing", "exciting", "can't wait"],
        "friendly": ["hi ", "thanks", "looking forward", "hope", "great"],
    }
    keywords = tone_keywords.get(tone.lower(), [])
    if not keywords:
        return 0.5
    matched = sum(1 for kw in keywords if kw in email_lower)
    return min(1.0, matched / len(keywords))


def tone_score(email: str, tone: str) -> float:
    try:
        judge_llm = get_judge_llm()
        result = judge_llm.invoke(_TONE_PROMPT.format(tone=tone, email=email))
        score = _extract_score(result.content)
        if score is None:
            raise ValueError(f"Judge returned no parseable number: {result.content!r}")
        return score
    except Exception:
        # Reachable now only for genuine reasons (no API key, network error,
        # judge gave a non-numeric reply) -- not because of the old env-var bug.
        return _keyword_tone_fallback(email.lower(), tone)


# Structure Score

_GREETING_RE = re.compile(r"\b(dear|hello|hi|greetings|good (morning|afternoon|evening))\b")
_CLOSING_RE = re.compile(r"\b(regards|sincerely|warmly)\b|\bbest,|\bbest regards\b|\bthank you\b|\bthanks,")


def structure_score(subject: str, body: str) -> float:
    """
    Signature changed from structure_score(email: str) to
    structure_score(subject: str, body: str).

    The old version checked a pre-built "Subject: {subject}\\n\\n{body}"
    string for the literal substring "subject:" -- which evaluate_email()
    always inserts itself, regardless of whether the model produced a real
    subject. That check was therefore *always true* and contributed a
    guaranteed, non-discriminating 0.3 points to every single email.
    Checking the actual subject field fixes that.
    """
    score = 0.0
    body_lower = body.lower()
    word_count = len(body.split())

    if subject.strip():
        score += 0.3

    # A reasonable length window -- a near-empty body shouldn't score the
    # same as a properly composed one just because it's "not too long".
    if 20 <= word_count <= 300:
        score += 0.3

    if _GREETING_RE.search(body_lower):
        score += 0.2

    if _CLOSING_RE.search(body_lower):
        score += 0.2

    return min(score, 1.0)


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def evaluate_email(email: dict, key_facts: list[str], tone: str) -> dict:
    subject = email.get("subject", "")
    body = email.get("body", "")
    full_email = f"Subject: {subject}\n\n{body}"

    fcs = fact_coverage_score(full_email, key_facts)
    tcs = tone_score(full_email, tone)
    css = structure_score(subject, body)

    return {
        "fact_coverage_score": round(fcs, 4),
        "tone_score": round(tcs, 4),
        "structure_score": round(css, 4),
        "avg": round((fcs + tcs + css) / 3, 4),
    }