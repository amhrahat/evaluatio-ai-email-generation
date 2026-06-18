import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import Email
from app.schemas import EmailCreate, EmailOut
from app.core.llm import generate_email

logger = logging.getLogger(__name__)


async def create_and_store_email(
    request: EmailCreate,
    db: Session
) -> EmailOut:
    """
    Generate email using LLM and store in database.
    
    Args:
        request: EmailCreate schema with intent, key_facts, tone
        db: Database session
        
    Returns:
        EmailOut schema with generated email
    """
    
    try:
        # Generate email using LangGraph + LLM with advanced prompting
        email_data = await generate_email(
            intent=request.intent,
            key_facts=request.key_facts,
            tone=request.tone
        )
        
        subject = email_data["subject"]
        body = email_data["body"]
        
        # Combine subject and body as per requirements
        combined_email = f"Subject: {subject}\n\n{body}"
        
        # Create Email model instance
        email_obj = Email(
            intents=request.intent,  # Store intent as provided
            key_facts=json.dumps(request.key_facts),  # Store as JSON string
            tone=request.tone,
            email=combined_email,
            subject=subject
        )
        
        # Persist to database
        db.add(email_obj)
        db.commit()
        db.refresh(email_obj)
        
        logger.info(f"Email generated and stored with ID: {email_obj.id}")
        
        return EmailOut(
            id=email_obj.id,
            intents=email_obj.intents,
            key_facts=json.loads(email_obj.key_facts),
            tone=email_obj.tone,
            subject=email_obj.subject,
            email=email_obj.email,
            created_at=email_obj.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating and storing email: {str(e)}")
        db.rollback()
        raise