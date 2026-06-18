import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Email(Base):
    """Email model for storing generated emails."""
    
    __tablename__ = "emails"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    intents = Column(String(500), nullable=False, index=True)  # space-separated intent keywords
    key_facts = Column(Text, nullable=False)  # JSON array stored as text
    tone = Column(String(50), nullable=False, index=True)  # formal, casual, urgent, empathetic, etc.
    email = Column(Text, nullable=False)  # combined subject + body
    subject = Column(String(500), nullable=False)  # extracted subject for quick reference
    created_at = Column(DateTime, default=datetime.timezone.utc, index=True)
    