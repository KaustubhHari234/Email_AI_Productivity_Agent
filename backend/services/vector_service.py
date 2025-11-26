"""Pinecone vector database service for RAG."""
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class VectorService:
    """Service for Pinecone vector operations."""

    def __init__(self):
        """Initialize Pinecone client."""
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self.dimension = settings.pinecone_dimension
        
        # Initialize embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=settings.gemini_api_key
        )
        
        # Ensure index exists
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        """Create index if it doesn't exist."""
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=settings.pinecone_metric,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment
                    )
                )
                logger.info("Index created successfully")
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using LangChain wrapper."""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def upsert_email(
        self,
        email_id: str,
        email_content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Upsert email into vector database."""
        try:
            embedding = self._generate_embedding(email_content)
            
            self.index.upsert(
                vectors=[
                    {
                        "id": email_id,
                        "values": embedding,
                        "metadata": metadata
                    }
                ]
            )
            
            logger.info(f"Upserted email {email_id} to vector DB")
            return email_id
        except Exception as e:
            logger.error(f"Error upserting email: {e}")
            raise

    async def search_similar_emails(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar emails."""
        try:
            query_embedding = self._generate_embedding(query)
            
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Error searching similar emails: {e}")
            raise

    async def delete_email(self, email_id: str):
        """Delete email from vector database."""
        try:
            self.index.delete(ids=[email_id])
            logger.info(f"Deleted email {email_id} from vector DB")
        except Exception as e:
            logger.error(f"Error deleting email: {e}")
            raise

    async def get_relevant_context(
        self,
        query: str,
        top_k: int = 3
    ) -> str:
        """Get relevant context for query."""
        results = await self.search_similar_emails(query, top_k=top_k)
        
        context_parts = []
        for result in results:
            metadata = result.get("metadata", {})
            email_text = f"""
Subject: {metadata.get('subject', 'N/A')}
From: {metadata.get('sender', 'N/A')}
Content: {metadata.get('body_preview', 'N/A')}
"""
            context_parts.append(email_text.strip())
        
        return "\n\n---\n\n".join(context_parts)
