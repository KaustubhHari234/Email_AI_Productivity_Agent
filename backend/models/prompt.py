"""Prompt configuration models."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PromptConfig(BaseModel):
    """Prompt configuration for agents."""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    name: str
    prompt_type: str  # categorization, action_item, reply_draft
    prompt_text: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    version: int = 1
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PromptLibrary(BaseModel):
    """Collection of prompt configurations."""
    categorization_prompt: Optional[PromptConfig] = None
    action_item_prompt: Optional[PromptConfig] = None
    reply_draft_prompt: Optional[PromptConfig] = None
