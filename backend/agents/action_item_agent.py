"""Action item extraction agent."""
import logging
from typing import List, Optional

from backend.models.email import Email, ActionItem
from backend.services.llm_service import LLMService
from backend.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class ActionItemAgent:
    """Agent for extracting action items from emails."""

    def __init__(self):
        """Initialize action item agent."""
        self.llm_service = LLMService()
        self.db_service = DatabaseService()

    async def extract_action_items(
        self,
        email: Email,
        custom_prompt: Optional[str] = None
    ) -> Email:
        """Extract action items from a single email."""
        try:
            email_content = f"""
Subject: {email.subject}
From: {email.sender}
To: {email.recipient}
Date: {email.timestamp}

Body:
{email.body}
"""
            
            # Get custom prompt if provided
            if not custom_prompt:
                prompt_config = await self.db_service.get_active_prompt("action_item")
                if prompt_config:
                    custom_prompt = prompt_config.prompt_text
            
            # Extract action items using LLM
            action_items_data = await self.llm_service.extract_action_items(
                email_content,
                custom_prompt=custom_prompt
            )
            
            # Convert to ActionItem objects
            email.action_items = [
                ActionItem(**item) for item in action_items_data
            ]
            
            # Save updated email
            await self.db_service.save_email(email)
            
            logger.info(f"Extracted {len(email.action_items)} action items from email {email.id}")
            return email
        except Exception as e:
            logger.error(f"Error extracting action items from email {email.id}: {e}")
            raise

    async def get_all_action_items(
        self,
        include_completed: bool = False
    ) -> List[dict]:
        """Get all action items from all emails."""
        try:
            emails = await self.db_service.get_all_emails(limit=1000)
            
            all_action_items = []
            for email in emails:
                for action_item in email.action_items:
                    if include_completed or not action_item.completed:
                        all_action_items.append({
                            "email_id": email.id,
                            "email_subject": email.subject,
                            "email_sender": email.sender,
                            "action_item": action_item.model_dump()
                        })
            
            # Sort by priority
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            all_action_items.sort(
                key=lambda x: priority_order.get(x["action_item"]["priority"], 3)
            )
            
            return all_action_items
        except Exception as e:
            logger.error(f"Error getting all action items: {e}")
            return []

    async def mark_action_item_complete(
        self,
        email_id: str,
        action_item_description: str
    ) -> bool:
        """Mark an action item as completed."""
        try:
            email = await self.db_service.get_email(email_id)
            if not email:
                logger.warning(f"Email {email_id} not found")
                return False
            
            for action_item in email.action_items:
                if action_item.description == action_item_description:
                    action_item.completed = True
                    await self.db_service.save_email(email)
                    logger.info(f"Marked action item as complete: {action_item_description}")
                    return True
            
            logger.warning(f"Action item not found: {action_item_description}")
            return False
        except Exception as e:
            logger.error(f"Error marking action item complete: {e}")
            return False

    async def get_action_items_by_priority(
        self,
        priority: str
    ) -> List[dict]:
        """Get action items filtered by priority."""
        all_items = await self.get_all_action_items()
        return [
            item for item in all_items
            if item["action_item"]["priority"] == priority
        ]
