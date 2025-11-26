"""Main backend orchestrator and API."""
import asyncio
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.config.settings import settings
from backend.models.email import Email, EmailCategory
from backend.models.prompt import PromptConfig
from backend.models.draft import EmailDraft
from backend.services.email_service import EmailService
from backend.services.database_service import DatabaseService
from backend.agents.categorization_agent import CategorizationAgent
from backend.agents.action_item_agent import ActionItemAgent
from backend.agents.draft_agent import DraftAgent
from backend.agents.rag_agent import RAGAgent

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Email Productivity Agent Backend")

class EmailProductivityBackend:
    """Main backend orchestrator."""

    def __init__(self):
        """Initialize backend services and agents."""
        self.email_service = EmailService()
        self.db_service = DatabaseService()
        
        # Initialize agents
        self.categorization_agent = CategorizationAgent()
        self.action_item_agent = ActionItemAgent()
        self.draft_agent = DraftAgent()
        self.rag_agent = RAGAgent()
        
        logger.info("Email Productivity Backend initialized")

    # Phase 1: Email Ingestion & Knowledge Base
    async def load_and_process_emails(
        self,
        source: str = "mock",
        file_path: Optional[str] = None
    ) -> List[Email]:
        """Load emails and process them through the pipeline."""
        try:
            # Load emails
            if source == "mock":
                emails = await self.email_service.load_mock_emails(
                    file_path or "data/mock_emails.json"
                )
            else:
                # Future: Support for real email connections
                raise NotImplementedError(f"Source '{source}' not yet supported")
            
            if not emails:
                logger.warning("No emails loaded")
                return []
            
            # Get active prompts
            cat_prompt = await self.db_service.get_active_prompt("categorization")
            action_prompt = await self.db_service.get_active_prompt("action_item")
            
            cat_prompt_text = cat_prompt.prompt_text if cat_prompt else None
            action_prompt_text = action_prompt.prompt_text if action_prompt else None
            
            # Process emails
            processed_emails = await self.email_service.process_email_batch(
                emails,
                categorization_prompt=cat_prompt_text,
                action_item_prompt=action_prompt_text
            )
            
            logger.info(f"Processed {len(processed_emails)} emails")
            return processed_emails
        except Exception as e:
            logger.error(f"Error loading and processing emails: {e}")
            raise

    async def get_emails(
        self,
        category: Optional[EmailCategory] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Email]:
        """Get emails with optional filtering."""
        return await self.db_service.get_all_emails(
            skip=skip,
            limit=limit,
            category=category
        )

    async def get_email_by_id(self, email_id: str) -> Optional[Email]:
        """Get specific email by ID."""
        return await self.db_service.get_email(email_id)

    # Prompt Management
    async def save_prompt_config(self, prompt_config: PromptConfig) -> str:
        """Save prompt configuration."""
        return await self.db_service.save_prompt(prompt_config)

    async def get_prompt_configs(self) -> List[PromptConfig]:
        """Get all prompt configurations."""
        return await self.db_service.get_all_prompts()

    async def get_active_prompts(self) -> dict:
        """Get all active prompts."""
        cat_prompt = await self.db_service.get_active_prompt("categorization")
        action_prompt = await self.db_service.get_active_prompt("action_item")
        reply_prompt = await self.db_service.get_active_prompt("reply_draft")
        
        return {
            "categorization": cat_prompt,
            "action_item": action_prompt,
            "reply_draft": reply_prompt
        }

    # Phase 2: Email Processing Agent (RAG)
    async def query_inbox(self, query: str) -> dict:
        """Query inbox using RAG agent."""
        return await self.rag_agent.answer_query(query)

    async def get_inbox_summary(self) -> str:
        """Get inbox summary."""
        return await self.rag_agent.summarize_inbox()

    async def find_urgent_emails(self) -> str:
        """Find urgent emails."""
        return await self.rag_agent.find_urgent_emails()

    async def search_by_sender(self, sender: str) -> str:
        """Search emails by sender."""
        return await self.rag_agent.get_emails_by_sender(sender)

    async def search_by_topic(self, topic: str) -> str:
        """Search emails by topic."""
        return await self.rag_agent.search_emails_by_topic(topic)

    async def summarize_email(self, email_id: str) -> str:
        """Get email summary."""
        return await self.email_service.get_email_summary(email_id)

    # Phase 3: Draft Generation
    async def generate_reply_draft(
        self,
        email_id: str,
        additional_context: Optional[str] = None
    ) -> EmailDraft:
        """Generate reply draft for an email."""
        email = await self.db_service.get_email(email_id)
        if not email:
            raise ValueError(f"Email {email_id} not found")
        
        return await self.draft_agent.generate_reply_draft(
            email,
            additional_context=additional_context
        )

    async def generate_new_draft(
        self,
        recipient: str,
        subject: str,
        instructions: str,
        context: Optional[str] = None
    ) -> EmailDraft:
        """Generate new email draft."""
        return await self.draft_agent.generate_new_draft(
            recipient=recipient,
            subject=subject,
            instructions=instructions,
            context=context
        )

    async def refine_draft(
        self,
        draft_id: str,
        refinement_instruction: str
    ) -> EmailDraft:
        """Refine existing draft."""
        draft = await self.db_service.get_draft(draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found")
        
        return await self.draft_agent.refine_draft(draft, refinement_instruction)

    async def get_all_drafts(self) -> List[EmailDraft]:
        """Get all drafts."""
        return await self.draft_agent.get_all_drafts()

    async def get_draft_by_id(self, draft_id: str) -> Optional[EmailDraft]:
        """Get specific draft."""
        return await self.db_service.get_draft(draft_id)

    async def delete_draft(self, draft_id: str):
        """Delete draft."""
        await self.draft_agent.delete_draft(draft_id)

    # Action Items
    async def get_all_action_items(
        self,
        include_completed: bool = False
    ) -> List[dict]:
        """Get all action items."""
        return await self.action_item_agent.get_all_action_items(include_completed)

    async def mark_action_item_complete(
        self,
        email_id: str,
        action_description: str
    ) -> bool:
        """Mark action item as complete."""
        return await self.action_item_agent.mark_action_item_complete(
            email_id,
            action_description
        )

    # Statistics
    async def get_category_statistics(self) -> dict:
        """Get category statistics."""
        return await self.categorization_agent.get_category_statistics()


# Initialize backend instance
backend = EmailProductivityBackend()

@app.on_event("startup")
async def startup_event():
    """Initialize backend resources on startup."""
    logger.info("Starting up Email Productivity Agent Backend...")
    # You might want to trigger initial data loading here if appropriate
    # await backend.load_and_process_emails()

@app.get("/")
async def root():
    return {"message": "Email Productivity Agent Backend is running"}

@app.post("/emails/process")
async def process_emails(source: str = "mock"):
    try:
        emails = await backend.load_and_process_emails(source=source)
        return {"message": f"Processed {len(emails)} emails", "count": len(emails)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails", response_model=List[Email])
async def get_emails(category: Optional[EmailCategory] = None, skip: int = 0, limit: int = 50):
    return await backend.get_emails(category, skip, limit)

@app.get("/emails/{email_id}", response_model=Email)
async def get_email(email_id: str):
    email = await backend.get_email_by_id(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@app.get("/inbox/summary")
async def get_inbox_summary():
    summary = await backend.get_inbox_summary()
    return {"summary": summary}

@app.get("/inbox/query")
async def query_inbox(q: str):
    return await backend.query_inbox(q)

@app.get("/action-items")
async def get_action_items(include_completed: bool = False):
    return await backend.get_all_action_items(include_completed)

@app.get("/drafts", response_model=List[EmailDraft])
async def get_drafts():
    return await backend.get_all_drafts()

# Main entry point for testing
async def main():
    """Main entry point for backend testing."""
    # Example: Load and process mock emails
    emails = await backend.load_and_process_emails()
    print(f"Loaded and processed {len(emails)} emails")
    
    # Example: Get inbox summary
    summary = await backend.get_inbox_summary()
    print(f"Inbox Summary: {summary}")
    
    # Example: Get all action items
    action_items = await backend.get_all_action_items()
    print(f"Found {len(action_items)} action items")


if __name__ == "__main__":
    asyncio.run(main())
