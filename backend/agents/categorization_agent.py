"""Email categorization agent."""
import logging
from typing import Optional

from backend.models.email import Email, EmailCategory
from backend.services.llm_service import LLMService
from backend.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class CategorizationAgent:
    """Agent for categorizing emails."""

    def __init__(self):
        """Initialize categorization agent."""
        self.llm_service = LLMService()
        self.db_service = DatabaseService()

    async def categorize_single_email(
        self,
        email: Email,
        custom_prompt: Optional[str] = None
    ) -> Email:
        """Categorize a single email."""
        try:
            email_content = f"""
Subject: {email.subject}
From: {email.sender}
To: {email.recipient}
Date: {email.timestamp}

Body:
{email.body}
"""
            
            # Get custom prompt if provided, otherwise use default
            if not custom_prompt:
                prompt_config = await self.db_service.get_active_prompt("categorization")
                if prompt_config:
                    custom_prompt = prompt_config.prompt_text
            
            # Categorize using LLM
            result = await self.llm_service.categorize_email(
                email_content,
                custom_prompt=custom_prompt
            )
            
            # Update email with categorization results
            try:
                email.category = EmailCategory(result.get('category', 'UNCATEGORIZED'))
            except ValueError:
                logger.warning(f"Invalid category: {result.get('category')}")
                email.category = EmailCategory.UNCATEGORIZED
            
            email.category_reason = result.get('reason', 'No reason provided')
            
            # Save updated email
            await self.db_service.save_email(email)
            
            logger.info(f"Categorized email {email.id} as {email.category.value}")
            return email
        except Exception as e:
            logger.error(f"Error categorizing email {email.id}: {e}")
            raise

    async def recategorize_all_emails(
        self,
        custom_prompt: Optional[str] = None
    ) -> int:
        """Recategorize all emails in database."""
        try:
            emails = await self.db_service.get_all_emails(limit=1000)
            count = 0
            
            for email in emails:
                try:
                    await self.categorize_single_email(email, custom_prompt)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to recategorize email {email.id}: {e}")
                    continue
            
            logger.info(f"Recategorized {count} emails")
            return count
        except Exception as e:
            logger.error(f"Error recategorizing emails: {e}")
            raise

    async def get_category_statistics(self) -> dict:
        """Get statistics for email categories."""
        try:
            stats = {}
            for category in EmailCategory:
                count = await self.db_service.get_email_count(category=category)
                stats[category.value] = count
            
            return stats
        except Exception as e:
            logger.error(f"Error getting category statistics: {e}")
            return {}
