"""Email loading and processing service."""
import json
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime

from backend.models.email import Email, EmailCategory, ActionItem
from backend.services.llm_service import LLMService
from backend.services.vector_service import VectorService
from backend.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class EmailService:
    """Service for email operations."""

    def __init__(self):
        """Initialize email service."""
        self.llm_service = LLMService()
        self.vector_service = VectorService()
        self.db_service = DatabaseService()

    async def load_mock_emails(self, file_path: str = "data/mock_emails.json") -> List[Email]:
        """Load emails from mock JSON file."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Mock email file not found: {file_path}")
                return []
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            emails = []
            for item in data:
                email = Email(
                    id=item.get('id', str(datetime.now().timestamp())),
                    sender=item['sender'],
                    recipient=item.get('recipient', 'user@company.com'),
                    subject=item['subject'],
                    body=item['body'],
                    timestamp=datetime.fromisoformat(item.get('timestamp', datetime.now().isoformat())),
                    has_attachments=item.get('has_attachments', False),
                    attachment_names=item.get('attachment_names', [])
                )
                emails.append(email)
            
            logger.info(f"Loaded {len(emails)} mock emails")
            return emails
        except Exception as e:
            logger.error(f"Error loading mock emails: {e}")
            return []

    async def process_email(
        self,
        email: Email,
        categorization_prompt: Optional[str] = None,
        action_item_prompt: Optional[str] = None
    ) -> Email:
        """Process single email through LLM pipeline."""
        try:
            email_content = f"Subject: {email.subject}\n\nBody: {email.body}"
            
            # Step 1: Categorize email
            logger.info(f"Categorizing email {email.id}")
            category_result = await self.llm_service.categorize_email(
                email_content,
                custom_prompt=categorization_prompt
            )
            
            email.category = EmailCategory(category_result.get('category', 'UNCATEGORIZED'))
            email.category_reason = category_result.get('reason', '')
            
            # Step 2: Extract action items
            logger.info(f"Extracting action items for email {email.id}")
            action_items = await self.llm_service.extract_action_items(
                email_content,
                custom_prompt=action_item_prompt
            )
            
            email.action_items = [
                ActionItem(**item) for item in action_items
            ]
            
            # Step 3: Save to database
            await self.db_service.save_email(email)
            
            # Step 4: Add to vector database for RAG
            metadata = {
                "sender": email.sender,
                "subject": email.subject,
                "body_preview": email.body[:200],
                "category": email.category.value,
                "timestamp": email.timestamp.isoformat()
            }
            
            email.embedding_id = await self.vector_service.upsert_email(
                email.id,
                email_content,
                metadata
            )
            
            logger.info(f"Successfully processed email {email.id}")
            return email
        except Exception as e:
            logger.error(f"Error processing email {email.id}: {e}")
            raise

    async def process_email_batch(
        self,
        emails: List[Email],
        categorization_prompt: Optional[str] = None,
        action_item_prompt: Optional[str] = None
    ) -> List[Email]:
        """Process batch of emails."""
        processed_emails = []
        
        for email in emails:
            try:
                processed_email = await self.process_email(
                    email,
                    categorization_prompt=categorization_prompt,
                    action_item_prompt=action_item_prompt
                )
                processed_emails.append(processed_email)
            except Exception as e:
                logger.error(f"Failed to process email {email.id}: {e}")
                continue
        
        return processed_emails

    async def get_email_summary(self, email_id: str) -> str:
        """Get email summary using LLM."""
        email = await self.db_service.get_email(email_id)
        if not email:
            return "Email not found"
        
        prompt = f"""Summarize this email in 2-3 sentences:

Subject: {email.subject}
From: {email.sender}
Body: {email.body}

Summary:"""

        summary = await self.llm_service.generate_text(prompt, temperature=0.3)
        return summary
