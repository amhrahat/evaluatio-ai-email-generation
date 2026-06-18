import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import EmailCreate, EmailOut
from app.services.email_service import create_and_store_email
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["emails"])


@router.post("/generate-email", response_model=EmailOut, status_code=201)
async def generate_email_endpoint(
    request: EmailCreate,
    db: Session = Depends(get_db)
) -> EmailOut:
    """
    Generate a professional email.
    
    **Request Body:**
    - **intent**: Core purpose of the email (string, 5-500 chars)
    - **key_facts**: List of facts to include (list of strings, 1-10 items)
    - **tone**: Desired tone - one of: formal, casual, urgent, empathetic, professional, friendly
    
    **Returns:**
    - **id**: Unique email identifier (UUID)
    - **intents**: The intent provided
    - **key_facts**: List of facts as provided
    - **tone**: The tone used
    - **subject**: Generated email subject
    - **email**: Full email (subject + body combined)
    - **created_at**: Timestamp of creation
    """
    try:
        return await create_and_store_email(request, db)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate email")


@router.get("/emails/{email_id}", response_model=EmailOut)
def get_email(email_id: str, db: Session = Depends(get_db)) -> EmailOut:
    """Retrieve a previously generated email by ID."""
    from app.db.models import Email
    
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return EmailOut(
        id=email.id,
        intents=email.intents,
        key_facts=__import__("json").loads(email.key_facts),
        tone=email.tone,
        subject=email.subject,
        email=email.email,
        created_at=email.created_at
    )


@router.get("/emails", response_model=list[EmailOut])
def list_emails(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> list[EmailOut]:
    """List recently generated emails."""
    from app.db.models import Email
    import json
    
    emails = db.query(Email).order_by(Email.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        EmailOut(
            id=e.id,
            intents=e.intents,
            key_facts=json.loads(e.key_facts),
            tone=e.tone,
            subject=e.subject,
            email=e.email,
            created_at=e.created_at
        )
        for e in emails
    ]