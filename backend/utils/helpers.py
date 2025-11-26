

"""Utility helper functions."""

import re
import hashlib
from datetime import datetime
from typing import Optional


def clean_email_address(email: str) -> str:
    """Clean and validate email address."""
    email = email.strip().lower()
    # Basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    return ""


def generate_email_id(sender: str, subject: str, timestamp: datetime) -> str:
    """Generate unique email ID."""
    content = f"{sender}_{subject}_{timestamp.isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime for display."""
    return dt.strftime(format_str)


def extract_email_preview(body: str, max_words: int = 30) -> str:
    """Extract preview from email body."""
    words = body.split()[:max_words]
    preview = " ".join(words)
    if len(body.split()) > max_words:
        preview += "..."
    return preview


def sanitize_html(text: str) -> str:
    """Basic HTML sanitization."""
    # Remove common HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    return text.strip()


def parse_email_signature(body: str) -> Optional[str]:
    """Try to extract email signature."""
    # Common signature indicators
    indicators = [
        r'\n--\s*\n',
        r'\nBest regards,',
        r'\nSincerely,',
        r'\nThanks,',
        r'\nRegards,'
    ]
    
    for indicator in indicators:
        match = re.search(indicator, body, re.IGNORECASE)
        if match:
            return body[match.start():].strip()
    
    return None


def calculate_urgency_score(email_body: str, subject: str) -> float:
    """Calculate urgency score based on keywords."""
    urgent_keywords = [
        'urgent', 'asap', 'immediate', 'critical', 'emergency',
        'important', 'priority', 'deadline', 'today', 'now'
    ]
    
    text = (email_body + " " + subject).lower()
    score = 0.0
    
    for keyword in urgent_keywords:
        if keyword in text:
            score += 0.2
    
    return min(score, 1.0)


def extract_mentioned_people(text: str) -> list:
    """Extract mentioned people/names from text."""
    # Simple pattern for @mentions
    mentions = re.findall(r'@([a-zA-Z0-9_]+)', text)
    return list(set(mentions))


def count_questions(text: str) -> int:
    """Count number of questions in text."""
    return text.count('?')
