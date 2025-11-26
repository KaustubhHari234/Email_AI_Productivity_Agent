"""Gemini LLM service integration."""
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import logging

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Google Gemini LLM."""

    def __init__(self):
        """Initialize Gemini service."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text completion."""
        try:
            generation_config = genai.GenerationConfig(
                temperature=temperature or settings.gemini_temperature,
                max_output_tokens=max_tokens or settings.gemini_max_tokens,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    async def categorize_email(
        self,
        email_content: str,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """Categorize email using LLM."""
        prompt = custom_prompt or settings.default_category_prompt
        full_prompt = f"""{prompt}

Email Content:
{email_content}

Respond in JSON format:
{{
    "category": "URGENT|ACTION_REQUIRED|INFORMATIONAL|SPAM",
    "reason": "brief explanation"
}}"""

        response = await self.generate_text(full_prompt, temperature=0.3)
        
        try:
            # Extract JSON from response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            result = json.loads(response_clean.strip())
            return result
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from categorization: {response}")
            return {"category": "UNCATEGORIZED", "reason": "Unable to categorize"}

    async def extract_action_items(
        self,
        email_content: str,
        custom_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract action items from email."""
        prompt = custom_prompt or settings.default_action_prompt
        full_prompt = f"""{prompt}

Email Content:
{email_content}

Respond in JSON format:
{{
    "action_items": [
        {{
            "description": "task description",
            "priority": "High|Medium|Low",
            "deadline": "deadline if mentioned or null"
        }}
    ]
}}"""

        response = await self.generate_text(full_prompt, temperature=0.3)
        
        try:
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            result = json.loads(response_clean.strip())
            return result.get("action_items", [])
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from action items: {response}")
            return []

    async def draft_reply(
        self,
        original_email: str,
        context: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Draft email reply."""
        prompt = custom_prompt or settings.default_reply_prompt
        
        context_str = f"\n\nAdditional Context:\n{context}" if context else ""
        
        full_prompt = f"""{prompt}

Original Email:
{original_email}
{context_str}

Draft Reply:"""

        response = await self.generate_text(full_prompt, temperature=0.7)
        return response.strip()

    async def answer_question(
        self,
        question: str,
        context: str
    ) -> str:
        """Answer question using provided context."""
        prompt = f"""Based on the following context, answer the question concisely and accurately.

Context:
{context}

Question: {question}

Answer:"""

        response = await self.generate_text(prompt, temperature=0.4)
        return response.strip()

    async def generate_with_stream(
        self,
        prompt: str,
        temperature: Optional[float] = None
    ):
        """Generate text with streaming."""
        try:
            generation_config = genai.GenerationConfig(
                temperature=temperature or settings.gemini_temperature,
                max_output_tokens=settings.gemini_max_tokens,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise