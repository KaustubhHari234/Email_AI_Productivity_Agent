"""Tests for service modules."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from backend.services.llm_service import LLMService
from backend.services.email_service import EmailService
from backend.models.email import Email, EmailCategory


@pytest.fixture
def llm_service():
    """Create LLM service instance."""
    return LLMService()


@pytest.fixture
def email_service():
    """Create email service instance."""
    return EmailService()


@pytest.fixture
def sample_email():
    """Create sample email."""
    return Email(
        id="test_001",
        sender="test@example.com",
        recipient="user@company.com",
        subject="Test Subject",
        body="This is a test email.",
        timestamp=datetime.now()
    )


class TestLLMService:
    """Tests for LLMService."""
    
    @pytest.mark.asyncio
    async def test_generate_text(self, llm_service):
        """Test text generation."""
        with patch.object(
            llm_service.model,
            'generate_content',
            return_value=Mock(text="Generated text")
        ):
            result = await llm_service.generate_text("Test prompt")
            
            assert result == "Generated text"
    
    @pytest.mark.asyncio
    async def test_categorize_email(self, llm_service):
        """Test email categorization."""
        mock_response = '{"category": "URGENT", "reason": "Time-sensitive"}'
        
        with patch.object(
            llm_service,
            'generate_text',
            new=AsyncMock(return_value=mock_response)
        ):
            result = await llm_service.categorize_email("Test email content")
            
            assert result["category"] == "URGENT"
            assert result["reason"] == "Time-sensitive"
    
    @pytest.mark.asyncio
    async def test_extract_action_items(self, llm_service):
        """Test action item extraction."""
        mock_response = '{"action_items": [{"description": "Task 1", "priority": "High", "deadline": null}]}'
        
        with patch.object(
            llm_service,
            'generate_text',
            new=AsyncMock(return_value=mock_response)
        ):
            result = await llm_service.extract_action_items("Test email content")
            
            assert len(result) == 1
            assert result[0]["description"] == "Task 1"


class TestEmailService:
    """Tests for EmailService."""
    
    @pytest.mark.asyncio
    async def test_load_mock_emails(self, email_service):
        """Test loading mock emails."""
        with patch('backend.services.email_service.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = '[]'
                
                # Since it's reading JSON, we need to mock json.load
                with patch('json.load', return_value=[]):
                    result = await email_service.load_mock_emails()
                    
                    assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_process_email(self, email_service, sample_email):
        """Test email processing."""
        with patch.object(
            email_service.llm_service,
            'categorize_email',
            new=AsyncMock(return_value={"category": "URGENT", "reason": "Test"})
        ):
            with patch.object(
                email_service.llm_service,
                'extract_action_items',
                new=AsyncMock(return_value=[])
            ):
                with patch.object(
                    email_service.db_service,
                    'save_email',
                    new=AsyncMock(return_value="test_001")
                ):
                    with patch.object(
                        email_service.vector_service,
                        'upsert_email',
                        new=AsyncMock(return_value="embed_001")
                    ):
                        result = await email_service.process_email(sample_email)
                        
                        assert result.category == EmailCategory.URGENT
                        assert result.embedding_id == "embed_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
