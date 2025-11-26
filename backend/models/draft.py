"""Draft email models."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


class EmailDraft(BaseModel):
    """Email draft model."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    original_email_id: Optional[str] = None
    recipient: str
    subject: str
    body: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Metadata
    category: Optional[str] = None
    action_items: List[str] = Field(default_factory=list)
    suggested_followups: List[str] = Field(default_factory=list)
    
    # Status
    is_sent: bool = False
    is_saved: bool = True
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_json_metadata(self) -> Dict[str, Any]:
        """Export draft with metadata as JSON."""
        return {
            "id": self.id,
            "original_email_id": self.original_email_id,
            "recipient": self.recipient,
            "subject": self.subject,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": {
                "category": self.category,
                "action_items": self.action_items,
                "suggested_followups": self.suggested_followups
            },
            "status": {
                "is_sent": self.is_sent,
                "is_saved": self.is_saved
            }
        }
