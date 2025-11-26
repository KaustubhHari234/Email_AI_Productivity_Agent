"""Email data models."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class EmailCategory(str, Enum):
    """Email category types."""
    URGENT = "URGENT"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    INFORMATIONAL = "INFORMATIONAL"
    SPAM = "SPAM"
    UNCATEGORIZED = "UNCATEGORIZED"


class ActionItem(BaseModel):
    """Action item extracted from email."""
    description: str
    priority: str = "Medium"  # High, Medium, Low
    deadline: Optional[str] = None
    completed: bool = False


class Email(BaseModel):
    """Email data model."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    sender: str
    recipient: str
    subject: str
    body: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Processing results
    category: EmailCategory = EmailCategory.UNCATEGORIZED
    category_reason: Optional[str] = None
    action_items: List[ActionItem] = Field(default_factory=list)
    
    # Metadata
    has_attachments: bool = False
    attachment_names: List[str] = Field(default_factory=list)
    thread_id: Optional[str] = None
    is_read: bool = False
    is_starred: bool = False
    
    # Vector search
    embedding_id: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmailBatch(BaseModel):
    """Batch of emails for processing."""
    emails: List[Email]
    total_count: int
    processed_count: int = 0
    
    
class EmailQuery(BaseModel):
    """Email query parameters."""
    category: Optional[EmailCategory] = None
    sender: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_action_items: Optional[bool] = None
    is_read: Optional[bool] = None
    search_text: Optional[str] = None
