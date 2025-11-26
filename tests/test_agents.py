"""Tests for agent modules."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from backend.agents.categorization_agent import CategorizationAgent
from backend.agents.action_item_agent import ActionItemAgent
from backend.agents.draft_agent import DraftAgent
from backend.agents.rag_agent import RAGAgent
from backend.models.email import Email, EmailCategory, ActionItem
from backend.models.draft import EmailDraft


@pytest.fixture
def sample_email():
    """Create sample email for testing."""
    return Email(
        id="test_001",
        sender="test@example.com",
        recipient="user@company.com",
        subject="Test Subject",
        body="This is a test email body with some content.",
        timestamp=datetime.now()
    )


@pytest.fixture
def categorization_agent():
    """Create categorization agent instance."""
    return CategorizationAgent()


@pytest.fixture
def action_item_agent():
    """Create action item agent instance."""
    return ActionItemAgent()


@pytest.fixture
def draft_agent():
    """Create draft agent instance."""
    return DraftAgent()


@pytest.fixture
def rag_agent():
    """Create RAG agent instance."""
    return RAGAgent()


class TestCategorizationAgent:
    """Tests for CategorizationAgent."""
    
    @pytest.mark.asyncio
    async def test_categorize_single_email(self, categorization_agent, sample_email):
        """Test email categorization."""
        with patch.object(
            categorization_agent.llm_service,
            'categorize_email',
            new=AsyncMock(return_value={"category": "ACTION_REQUIRED", "reason": "Test reason"})
        ):
            with patch.object(
                categorization_agent.db_service,
                'save_email',
                new=AsyncMock(return_value="test_001")
            ):
                result = await categorization_agent.categorize_single_email(sample_email)
                
                assert result.category == EmailCategory.ACTION_REQUIRED
                assert result.category_reason == "Test reason"
    
    @pytest.mark.asyncio
    async def test_get_category_statistics(self, categorization_agent):
        """Test category statistics retrieval."""
        with patch.object(
            categorization_agent.db_service,
            'get_email_count',
            new=AsyncMock(return_value=5)
        ):
            stats = await categorization_agent.get_category_statistics()
            
            assert isinstance(stats, dict)
            assert all(cat.value in stats for cat in EmailCategory)


class TestActionItemAgent:
    """Tests for ActionItemAgent."""
    
    @pytest.mark.asyncio
    async def test_extract_action_items(self, action_item_agent, sample_email):
        """Test action item extraction."""
        mock_items = [
            {"description": "Test task", "priority": "High", "deadline": None}
        ]
        
        with patch.object(
            action_item_agent.llm_service,
            'extract_action_items',
            new=AsyncMock(return_value=mock_items)
        ):
            with patch.object(
                action_item_agent.db_service,
                'save_email',
                new=AsyncMock(return_value="test_001")
            ):
                result = await action_item_agent.extract_action_items(sample_email)
                
                assert len(result.action_items) == 1
                assert result.action_items[0].description == "Test task"
                assert result.action_items[0].priority == "High"
    
    @pytest.mark.asyncio
    async def test_mark_action_item_complete(self, action_item_agent, sample_email):
        """Test marking action item as complete."""
        sample_email.action_items = [
            ActionItem(description="Test task", priority="High")
        ]
        
        with patch.object(
            action_item_agent.db_service,
            'get_email',
            new=AsyncMock(return_value=sample_email)
        ):
            with patch.object(
                action_item_agent.db_service,
                'save_email',
                new=AsyncMock(return_value="test_001")
            ):
                result = await action_item_agent.mark_action_item_complete(
                    "test_001",
                    "Test task"
                )
                
                assert result is True


class TestDraftAgent:
    """Tests for DraftAgent."""
    
    @pytest.mark.asyncio
    async def test_generate_reply_draft(self, draft_agent, sample_email):
        """Test reply draft generation."""
        with patch.object(
            draft_agent.llm_service,
            'draft_reply',
            new=AsyncMock(return_value="This is a test reply.")
        ):
            with patch.object(
                draft_agent,
                '_generate_followups',
                new=AsyncMock(return_value=["Follow up 1", "Follow up 2"])
            ):
                with patch.object(
                    draft_agent.db_service,
                    'save_draft',
                    new=AsyncMock(return_value="draft_001")
                ):
                    result = await draft_agent.generate_reply_draft(sample_email)
                    
                    assert isinstance(result, EmailDraft)
                    assert result.subject.startswith("Re:")
                    assert result.recipient == sample_email.sender
                    assert result.body == "This is a test reply."
    
    @pytest.mark.asyncio
    async def test_generate_new_draft(self, draft_agent):
        """Test new draft generation."""
        with patch.object(
            draft_agent.llm_service,
            'generate_text',
            new=AsyncMock(return_value="This is a new draft.")
        ):
            with patch.object(
                draft_agent.db_service,
                'save_draft',
                new=AsyncMock(return_value="draft_002")
            ):
                result = await draft_agent.generate_new_draft(
                    recipient="test@example.com",
                    subject="Test Subject",
                    instructions="Write a professional email"
                )
                
                assert isinstance(result, EmailDraft)
                assert result.recipient == "test@example.com"
                assert result.subject == "Test Subject"


class TestRAGAgent:
    """Tests for RAGAgent."""
    
    @pytest.mark.asyncio
    async def test_answer_query(self, rag_agent):
        """Test query answering."""
        with patch.object(
            rag_agent.vector_service,
            'get_relevant_context',
            new=AsyncMock(return_value="Context about emails")
        ):
            with patch.object(
                rag_agent.llm_service,
                'answer_question',
                new=AsyncMock(return_value="This is the answer")
            ):
                with patch.object(
                    rag_agent.vector_service,
                    'search_similar_emails',
                    new=AsyncMock(return_value=[])
                ):
                    result = await rag_agent.answer_query("What is the status?")
                    
                    assert "answer" in result
                    assert result["answer"] == "This is the answer"
                    assert "sources" in result
    
    @pytest.mark.asyncio
    async def test_summarize_inbox(self, rag_agent, sample_email):
        """Test inbox summarization."""
        with patch.object(
            rag_agent.db_service,
            'get_all_emails',
            new=AsyncMock(return_value=[sample_email])
        ):
            with patch.object(
                rag_agent.llm_service,
                'generate_text',
                new=AsyncMock(return_value="Inbox summary")
            ):
                result = await rag_agent.summarize_inbox()
                
                assert result == "Inbox summary"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
