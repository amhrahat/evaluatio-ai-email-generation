from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class EmailCreate(BaseModel):
    """Request schema for email generation."""
    
    intent: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Core purpose of the email (e.g., 'Follow up after meeting')"
    )
    key_facts: list[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of facts/points to include in the email"
    )
    tone: str = Field(
        ...,
        description="Desired email tone (formal, casual, urgent, empathetic)"
    )


class EmailOut(BaseModel):
    """Response schema for generated email."""
    
    id: str
    intents: str
    key_facts: list[str]
    tone: str
    subject: str
    email: str  # combined subject + body
    created_at: datetime
    