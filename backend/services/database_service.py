"""MongoDB database service."""
from pymongo import MongoClient, ASCENDING, DESCENDING
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from backend.config.settings import settings
from backend.models.email import Email, EmailCategory
from backend.models.prompt import PromptConfig
from backend.models.draft import EmailDraft

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for MongoDB operations."""

    def __init__(self):
        """Initialize MongoDB client."""
        self.client = MongoClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_database]
        
        # Collections
        self.emails = self.db.emails
        self.prompts = self.db.prompts
        self.drafts = self.db.drafts
        
        # Create indexes
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes."""
        try:
            # Email indexes
            self.emails.create_index([("id", ASCENDING)], unique=True)
            self.emails.create_index([("sender", ASCENDING)])
            self.emails.create_index([("timestamp", DESCENDING)])
            self.emails.create_index([("category", ASCENDING)])
            
            # Prompt indexes
            self.prompts.create_index([("id", ASCENDING)], unique=True)
            self.prompts.create_index([("prompt_type", ASCENDING)])
            
            # Draft indexes
            self.drafts.create_index([("id", ASCENDING)], unique=True)
            self.drafts.create_index([("original_email_id", ASCENDING)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")

    # Email operations
    async def save_email(self, email: Email) -> str:
        """Save email to database."""
        try:
            email_dict = email.model_dump(mode='json')
            self.emails.update_one(
                {"id": email.id},
                {"$set": email_dict},
                upsert=True
            )
            return email.id
        except Exception as e:
            logger.error(f"Error saving email: {e}")
            raise

    async def get_email(self, email_id: str) -> Optional[Email]:
        """Get email by ID."""
        try:
            result = self.emails.find_one({"id": email_id})
            if result:
                result.pop('_id', None)
                return Email(**result)
            return None
        except Exception as e:
            logger.error(f"Error getting email: {e}")
            return None

    async def get_all_emails(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[EmailCategory] = None
    ) -> List[Email]:
        """Get all emails with optional filtering."""
        try:
            query = {}
            if category:
                query["category"] = category.value
            
            cursor = self.emails.find(query).sort("timestamp", DESCENDING).skip(skip).limit(limit)
            
            emails = []
            for doc in cursor:
                doc.pop('_id', None)
                emails.append(Email(**doc))
            
            return emails
        except Exception as e:
            logger.error(f"Error getting all emails: {e}")
            return []

    async def search_emails(
        self,
        query: Dict[str, Any],
        skip: int = 0,
        limit: int = 50
    ) -> List[Email]:
        """Search emails with custom query."""
        try:
            cursor = self.emails.find(query).sort("timestamp", DESCENDING).skip(skip).limit(limit)
            
            emails = []
            for doc in cursor:
                doc.pop('_id', None)
                emails.append(Email(**doc))
            
            return emails
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []

    async def get_email_count(self, category: Optional[EmailCategory] = None) -> int:
        """Get email count."""
        try:
            query = {}
            if category:
                query["category"] = category.value
            return self.emails.count_documents(query)
        except Exception as e:
            logger.error(f"Error getting email count: {e}")
            return 0

    # Prompt operations
    async def save_prompt(self, prompt: PromptConfig) -> str:
        """Save prompt configuration."""
        try:
            prompt_dict = prompt.model_dump(mode='json')
            self.prompts.update_one(
                {"id": prompt.id},
                {"$set": prompt_dict},
                upsert=True
            )
            return prompt.id
        except Exception as e:
            logger.error(f"Error saving prompt: {e}")
            raise

    async def get_active_prompt(self, prompt_type: str) -> Optional[PromptConfig]:
        """Get active prompt by type."""
        try:
            result = self.prompts.find_one({
                "prompt_type": prompt_type,
                "is_active": True
            })
            if result:
                result.pop('_id', None)
                return PromptConfig(**result)
            return None
        except Exception as e:
            logger.error(f"Error getting active prompt: {e}")
            return None

    async def get_all_prompts(self) -> List[PromptConfig]:
        """Get all prompts."""
        try:
            cursor = self.prompts.find().sort("created_at", DESCENDING)
            
            prompts = []
            for doc in cursor:
                doc.pop('_id', None)
                prompts.append(PromptConfig(**doc))
            
            return prompts
        except Exception as e:
            logger.error(f"Error getting all prompts: {e}")
            return []

    # Draft operations
    async def save_draft(self, draft: EmailDraft) -> str:
        """Save email draft."""
        try:
            draft.updated_at = datetime.now()
            draft_dict = draft.model_dump(mode='json')
            self.drafts.update_one(
                {"id": draft.id},
                {"$set": draft_dict},
                upsert=True
            )
            return draft.id
        except Exception as e:
            logger.error(f"Error saving draft: {e}")
            raise

    async def get_draft(self, draft_id: str) -> Optional[EmailDraft]:
        """Get draft by ID."""
        try:
            result = self.drafts.find_one({"id": draft_id})
            if result:
                result.pop('_id', None)
                return EmailDraft(**result)
            return None
        except Exception as e:
            logger.error(f"Error getting draft: {e}")
            return None

    async def get_all_drafts(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[EmailDraft]:
        """Get all drafts."""
        try:
            cursor = self.drafts.find().sort("updated_at", DESCENDING).skip(skip).limit(limit)
            
            drafts = []
            for doc in cursor:
                doc.pop('_id', None)
                drafts.append(EmailDraft(**doc))
            
            return drafts
        except Exception as e:
            logger.error(f"Error getting all drafts: {e}")
            return []

    async def delete_draft(self, draft_id: str):
        """Delete draft."""
        try:
            self.drafts.delete_one({"id": draft_id})
            logger.info(f"Deleted draft {draft_id}")
        except Exception as e:
            logger.error(f"Error deleting draft: {e}")
            raise
