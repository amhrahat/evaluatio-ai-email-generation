import os
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()


class EmailOutput(BaseModel):
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")


llm2 = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model=os.getenv("MODEL2"),
    temperature=float(os.getenv("TEMPERATURE", 0.7)),
)

structured_llm2 = llm2.with_structured_output(EmailOutput)




prompt2 = PromptTemplate(
    input_variables=["intent", "key_facts", "tone"],
    template="""
Write an email based on the following information.

Intent: {intent}

Facts:
{key_facts}

Tone:
{tone}
"""
)
async def generate_email2(intent: str, key_facts: list[str], tone: str):
    formatted_facts = "\n".join(f"- {fact}" for fact in key_facts)

    final_prompt2 = prompt2.format(
        intent=intent,
        key_facts=formatted_facts,
        tone=tone
    )

    result2 = structured_llm2.invoke(final_prompt2)

    return {
        "subject": result2.subject,
        "body": result2.body,
 
    }