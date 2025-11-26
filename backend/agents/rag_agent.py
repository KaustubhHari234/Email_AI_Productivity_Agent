"""RAG (Retrieval-Augmented Generation) agent for email queries."""
import logging
from typing import Optional

from backend.services.llm_service import LLMService
from backend.services.vector_service import VectorService
from backend.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class RAGAgent:
    """Agent for answering questions using RAG."""

    def __init__(self):
        """Initialize RAG agent."""
        self.llm_service = LLMService()
        self.vector_service = VectorService()
        self.db_service = DatabaseService()

    async def answer_query(
        self,
        query: str,
        top_k: int = 5
    ) -> dict:
        """Answer a query using RAG."""
        try:
            # Get relevant context from vector database
            relevant_context = await self.vector_service.get_relevant_context(
                query,
                top_k=top_k
            )
            
            if not relevant_context:
                return {
                    "answer": "I don't have enough information to answer that question. Please try rephrasing or check if emails have been processed.",
                    "sources": [],
                    "confidence": "low"
                }
            
            # Generate answer using LLM
            answer = await self.llm_service.answer_question(
                question=query,
                context=relevant_context
            )
            
            # Get source emails
            sources = await self.vector_service.search_similar_emails(query, top_k=3)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": "high" if len(sources) >= 2 else "medium"
            }
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "confidence": "error"
            }

    async def summarize_inbox(self, max_emails: int = 20) -> str:
        """Summarize inbox contents."""
        try:
            emails = await self.db_service.get_all_emails(limit=max_emails)
            
            if not emails:
                return "Your inbox is empty."
            
            # Prepare summary prompt
            email_summaries = []
            for email in emails[:10]:  # Limit to 10 for summary
                email_summaries.append(
                    f"- From {email.sender}: {email.subject} [{email.category.value}]"
                )
            
            prompt = f"""Summarize this inbox:

Total emails: {len(emails)}

Recent emails:
{chr(10).join(email_summaries)}

Provide a brief summary (2-3 sentences) of the inbox status and key items:"""

            summary = await self.llm_service.generate_text(prompt, temperature=0.5)
            
            return summary
        except Exception as e:
            logger.error(f"Error summarizing inbox: {e}")
            return "Error generating inbox summary."

    async def find_urgent_emails(self) -> str:
        """Find and summarize urgent emails."""
        try:
            query = "urgent important immediate action required critical"
            
            results = await self.vector_service.search_similar_emails(
                query,
                top_k=5
            )
            
            if not results:
                return "No urgent emails found."
            
            urgent_items = []
            for result in results:
                metadata = result.get("metadata", {})
                urgent_items.append(
                    f"- {metadata.get('subject', 'No subject')} from {metadata.get('sender', 'Unknown')}"
                )
            
            response = "Urgent/Important emails:\n" + "\n".join(urgent_items)
            return response
        except Exception as e:
            logger.error(f"Error finding urgent emails: {e}")
            return "Error finding urgent emails."

    async def get_emails_by_sender(self, sender: str) -> str:
        """Get emails from a specific sender."""
        try:
            emails = await self.db_service.search_emails(
                {"sender": {"$regex": sender, "$options": "i"}},
                limit=10
            )
            
            if not emails:
                return f"No emails found from {sender}."
            
            email_list = []
            for email in emails:
                email_list.append(
                    f"- {email.subject} ({email.timestamp.strftime('%Y-%m-%d')})"
                )
            
            response = f"Emails from {sender}:\n" + "\n".join(email_list)
            return response
        except Exception as e:
            logger.error(f"Error getting emails by sender: {e}")
            return f"Error retrieving emails from {sender}."

    async def search_emails_by_topic(self, topic: str) -> str:
        """Search emails related to a topic."""
        try:
            results = await self.vector_service.search_similar_emails(
                topic,
                top_k=5
            )
            
            if not results:
                return f"No emails found related to '{topic}'."
            
            email_list = []
            for result in results:
                metadata = result.get("metadata", {})
                score = result.get("score", 0)
                email_list.append(
                    f"- {metadata.get('subject', 'No subject')} (Relevance: {score:.2f})"
                )
            
            response = f"Emails related to '{topic}':\n" + "\n".join(email_list)
            return response
        except Exception as e:
            logger.error(f"Error searching emails by topic: {e}")
            return f"Error searching for '{topic}'."
