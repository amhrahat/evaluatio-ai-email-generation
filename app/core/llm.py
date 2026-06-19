import os
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()


class EmailOutput(BaseModel):
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")


llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model=os.getenv("MODEL1"),
    temperature=float(os.getenv("TEMPERATURE", 0.7)),
)

structured_llm = llm.with_structured_output(EmailOutput)

prompt = PromptTemplate(
    input_variables=["intent", "key_facts", "tone"],
    template="""
You are a Professional Email Assistant. Your role is to craft well-written, 
professional emails that seamlessly integrate key facts while maintaining the desired tone.

Now, generate a professional email based on the following inputs:

Intent: {intent}
Key Facts:
{key_facts}
Tone: {tone}

INSTRUCTIONS:
1. CAREFULLY READ the intent and understand the core purpose.
2. REVIEW each key fact and ensure ALL of them are seamlessly woven into the email (not listed).
3. MATCH the tone throughout the email (formal, casual, urgent, empathetic).
4. CREATE a concise, relevant subject line.
5. COMPOSE the body to flow naturally while respecting the tone.
6. RETURN your response as valid JSON with "subject" and "body" keys only.

Ensure your response is ONLY valid JSON, no additional text or markdown."""
)


async def generate_email(intent: str, key_facts: list[str], tone: str):
    formatted_facts = "\n".join(f"- {fact}" for fact in key_facts)

    final_prompt = prompt.format(
        intent=intent,
        key_facts=formatted_facts,
        tone=tone
    )

    result = structured_llm.invoke(final_prompt)

    return {
        "subject": result.subject,
        "body": result.body
    }