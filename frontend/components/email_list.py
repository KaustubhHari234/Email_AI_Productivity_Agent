"""Email list component for Streamlit."""
import streamlit as st
from typing import List, Optional
from datetime import datetime

from backend.models.email import Email, EmailCategory


def render_email_list(
    emails: List[Email],
    on_select_callback=None,
    selected_email_id: Optional[str] = None
):
    """Render email list with selection capability."""
    
    if not emails:
        st.info("📭 No emails to display. Load emails from the sidebar.")
        return
    
    st.subheader(f"📧 Inbox ({len(emails)} emails)")
    
    # Category filter
    col1, col2 = st.columns([3, 1])
    with col1:
        filter_category = st.selectbox(
            "Filter by category",
            options=["All"] + [cat.value for cat in EmailCategory],
            key="email_list_filter"
        )
    with col2:
        sort_order = st.selectbox(
            "Sort by",
            options=["Newest", "Oldest", "Category"],
            key="email_list_sort"
        )
    
    # Filter emails
    filtered_emails = emails
    if filter_category != "All":
        filtered_emails = [
            e for e in emails
            if e.category.value == filter_category
        ]
    
    # Sort emails
    if sort_order == "Category":
        # Define priority (lower number = higher priority)
        category_priority = {
            EmailCategory.URGENT: 1,
            EmailCategory.ACTION_REQUIRED: 2,
            EmailCategory.INFORMATIONAL: 3,
            EmailCategory.UNCATEGORIZED: 4,
            EmailCategory.SPAM: 5
        }
        
        filtered_emails = sorted(
            filtered_emails,
            key=lambda x: (category_priority.get(x.category, 99), x.timestamp),
            reverse=False # We want 1 -> 5, but for timestamp we might want newest first?
                          # Actually, let's keep it simple: Priority ASC, then Timestamp DESC (Newest first within category)
        )
        # To achieve Priority ASC and Timestamp DESC, we can use a tuple key with negated timestamp
        filtered_emails = sorted(
            filtered_emails,
            key=lambda x: (category_priority.get(x.category, 99), -x.timestamp.timestamp())
        )
    else:
        filtered_emails = sorted(
            filtered_emails,
            key=lambda x: x.timestamp,
            reverse=(sort_order == "Newest")
        )
    
    st.markdown("---")
    
    # Display emails
    for email in filtered_emails:
        render_email_card(
            email,
            is_selected=(email.id == selected_email_id),
            on_select=on_select_callback
        )


def render_email_card(
    email: Email,
    is_selected: bool = False,
    on_select=None
):
    """Render individual email card."""
    
    # Category color mapping
    category_colors = {
        EmailCategory.URGENT: "🔴",
        EmailCategory.ACTION_REQUIRED: "🟡",
        EmailCategory.INFORMATIONAL: "🔵",
        EmailCategory.SPAM: "⚫",
        EmailCategory.UNCATEGORIZED: "⚪"
    }
    
    category_icon = category_colors.get(email.category, "⚪")
    
    # Card container
    card_style = """
    <style>
    .email-card {
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
        background-color: #f9f9f9;
        cursor: pointer;
        transition: all 0.2s;
    }
    .email-card:hover {
        background-color: #f0f0f0;
        border-color: #1f77b4;
    }
    .email-card.selected {
        background-color: #e6f3ff;
        border-color: #1f77b4;
        border-width: 2px;
    }
    .email-sender {
        font-weight: bold;
        color: #333;
    }
    .email-subject {
        font-size: 14px;
        color: #555;
        margin: 5px 0;
    }
    .email-meta {
        font-size: 12px;
        color: #888;
    }
    .email-preview {
        font-size: 12px;
        color: #666;
        font-style: italic;
        margin-top: 5px;
    }
    </style>
    """
    
    st.markdown(card_style, unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([0.9, 0.1])
        
        with col1:
            # Email header
            st.markdown(f"**{category_icon} {email.sender}**")
            st.markdown(f"*{email.subject}*")
            
            # Metadata
            timestamp_str = email.timestamp.strftime("%b %d, %Y %I:%M %p")
            st.caption(f"📅 {timestamp_str} | 🏷️ {email.category.value}")
            
            # Action items badge
            if email.action_items:
                st.caption(f"✅ {len(email.action_items)} action item(s)")
            
            # Preview
            preview = email.body[:100] + "..." if len(email.body) > 100 else email.body
            st.caption(f"💬 {preview}")
        
        with col2:
            if st.button("📖", key=f"select_{email.id}", help="View email"):
                if on_select:
                    on_select(email.id)
        
        st.markdown("---")


def render_email_details(email: Email):
    """Render detailed email view."""
    
    st.subheader("📧 Email Details")
    
    # Header information
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**From:** {email.sender}")
        st.markdown(f"**To:** {email.recipient}")
    with col2:
        st.markdown(f"**Date:** {email.timestamp.strftime('%B %d, %Y %I:%M %p')}")
        st.markdown(f"**Category:** {email.category.value}")
    
    st.markdown("---")
    
    # Subject
    st.markdown(f"### {email.subject}")
    
    # Body
    st.markdown("**Message:**")
    st.text_area(
        "Email body",
        value=email.body,
        height=300,
        disabled=True,
        label_visibility="collapsed"
    )
    
    # Category reason
    if email.category_reason:
        with st.expander("📊 Categorization Details"):
            st.info(f"**Reason:** {email.category_reason}")
    
    # Action items
    if email.action_items:
        with st.expander(f"✅ Action Items ({len(email.action_items)})"):
            for idx, item in enumerate(email.action_items, 1):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    status = "✅" if item.completed else "⬜"
                    st.markdown(f"{status} {item.description}")
                with col2:
                    priority_colors = {
                        "High": "🔴",
                        "Medium": "🟡",
                        "Low": "🟢"
                    }
                    st.caption(f"{priority_colors.get(item.priority, '⚪')} {item.priority}")
                with col3:
                    if item.deadline:
                        st.caption(f"📅 {item.deadline}")
    
    # Attachments
    if email.has_attachments:
        with st.expander(f"📎 Attachments ({len(email.attachment_names)})"):
            for attachment in email.attachment_names:
                st.markdown(f"- {attachment}")
