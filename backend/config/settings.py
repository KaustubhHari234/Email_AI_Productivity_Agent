"""Application configuration management."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 2048
    embedding_model: str = "models/text-embedding-004"

    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "email-agent"
    pinecone_dimension: int = 768
    pinecone_metric: str = "cosine"

    # MongoDB Configuration
    mongodb_uri: Optional[str] = None
    mongodb_database: Optional[str] = None

    # Application Settings
    log_level: str = "INFO"
    max_emails_display: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Email Processing
    default_category_prompt: str = """You are an email categorization assistant. 
    Categorize the email into one of these categories: 
    - URGENT: Requires immediate attention
    - ACTION_REQUIRED: Needs response or action
    - INFORMATIONAL: FYI, no action needed
    - SPAM: Unwanted or promotional
    
    Provide category and brief reason."""

    default_action_prompt: str = """Extract action items from this email. 
    List each action item with:
    - Description of the task
    - Priority (High/Medium/Low)
    - Deadline if mentioned
    
    If no action items, respond with "No action items found"."""

    default_reply_prompt: str = """Draft a professional email reply based on:
    - Original email context
    - Professional and courteous tone
    - Address all key points
    - Keep it concise (2-3 paragraphs)
    
    Do not include subject line."""


# Global settings instance
settings = Settings()
