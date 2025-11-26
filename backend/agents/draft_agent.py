"""Email draft generation agent."""
import logging
from typing import Optional, List
from datetime import datetime

from backend.models.email import Email
from backend.models.draft import EmailDraft
from backend.services.llm_service import LLMService
from backend.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class DraftAgent:
    """Agent for generating email drafts."""

    def __init__(self):
        """Initialize draft agent."""
        self.llm_service = LLMService()
        self.db_service = DatabaseService()

    async def generate_reply_draft(
        self,
        original_email: Email,
        additional_context: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> EmailDraft:
        """Generate a reply draft for an email."""
        try:
            # Get custom prompt if not provided
            if not custom_prompt:
                prompt_config = await self.db_service.get_active_prompt("reply_draft")
                if prompt_config:
                    custom_prompt = prompt_config.prompt_text
            
            # Prepare original email content
            original_content = f"""
Subject: {original_email.subject}
From: {original_email.sender}
Date: {original_email.timestamp}

{original_email.body}
"""
            
            # Generate reply body
            reply_body = await self.llm_service.draft_reply(
                original_email=original_content,
                context=additional_context,
                custom_prompt=custom_prompt
            )
            
            # Generate subject line
            subject = f"Re: {original_email.subject}"
            if original_email.subject.startswith("Re: "):
                subject = original_email.subject
            
            # Generate suggested follow-ups
            followups = await self._generate_followups(original_email, reply_body)
            
            # Create draft
            draft = EmailDraft(
                original_email_id=original_email.id,
                recipient=original_email.sender,
                subject=subject,
                body=reply_body,
                category=original_email.category.value,
                action_items=[item.description for item in original_email.action_items],
                suggested_followups=followups
            )
            
            # Save draft
            await self.db_service.save_draft(draft)
            
            logger.info(f"Generated reply draft {draft.id} for email {original_email.id}")
            return draft
        except Exception as e:
            logger.error(f"Error generating reply draft: {e}")
            raise

    async def generate_new_draft(
        self,
        recipient: str,
        subject: str,
        instructions: str,
        context: Optional[str] = None
    ) -> EmailDraft:
        """Generate a new email draft from instructions."""
        try:
            prompt = f"""Write a professional email with the following details:

Recipient: {recipient}
Subject: {subject}
Instructions: {instructions}
{f"Context: {context}" if context else ""}

Write only the email body (no subject line):"""

            body = await self.llm_service.generate_text(prompt, temperature=0.7)
            
            draft = EmailDraft(
                recipient=recipient,
                subject=subject,
                body=body.strip()
            )
            
            await self.db_service.save_draft(draft)
            
            logger.info(f"Generated new draft {draft.id}")
            return draft
        except Exception as e:
            logger.error(f"Error generating new draft: {e}")
            raise

    async def _generate_followups(
        self,
        original_email: Email,
        reply_body: str
    ) -> List[str]:
        """Generate suggested follow-up actions."""
        try:
            prompt = f"""Based on this email conversation, suggest 2-3 brief follow-up actions:

Original Email:
Subject: {original_email.subject}
{original_email.body[:300]}

Reply:
{reply_body[:300]}

List follow-up actions (one per line):"""

            response = await self.llm_service.generate_text(prompt, temperature=0.6)
            
            # Parse response into list
            followups = [
                line.strip().lstrip('-•*').strip()
                for line in response.split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            
            return followups[:3]  # Limit to 3 suggestions
        except Exception as e:
            logger.warning(f"Error generating follow-ups: {e}")
            return []

    async def refine_draft(
        self,
        draft: EmailDraft,
        refinement_instruction: str
    ) -> EmailDraft:
        """Refine an existing draft based on instructions."""
        try:
            prompt = f"""Refine this email draft based on the instruction:

Current Draft:
Subject: {draft.subject}
Body:
{draft.body}

Instruction: {refinement_instruction}

Refined email body:"""

            refined_body = await self.llm_service.generate_text(prompt, temperature=0.7)
            
            draft.body = refined_body.strip()
            draft.updated_at = datetime.now()
            
            await self.db_service.save_draft(draft)
            
            logger.info(f"Refined draft {draft.id}")
            return draft
        except Exception as e:
            logger.error(f"Error refining draft: {e}")
            raise

    async def get_all_drafts(self) -> List[EmailDraft]:
        """Get all saved drafts."""
        return await self.db_service.get_all_drafts()

    async def delete_draft(self, draft_id: str):
        """Delete a draft."""
        await self.db_service.delete_draft(draft_id)
        logger.info(f"Deleted draft {draft_id}")
