"""Draft editor component."""
import streamlit as st
import json
import asyncio
from typing import Optional

from backend.models.draft import EmailDraft


def render_draft_editor(backend, email_id: Optional[str] = None):
    """Render draft editor interface."""
    
    st.subheader("✉️ Draft Email")
    
    # Tabs for different draft modes
    tab1, tab2, tab3 = st.tabs([
        "📝 New Draft",
        "↩️ Reply Draft",
        "💾 Saved Drafts"
    ])
    
    with tab1:
        render_new_draft_editor(backend)
    
    with tab2:
        render_reply_draft_editor(backend, email_id)
    
    with tab3:
        render_saved_drafts(backend)


def render_new_draft_editor(backend):
    """Render new draft creation interface."""
    
    st.markdown("### Create New Email Draft")
    
    recipient = st.text_input(
        "To:",
        placeholder="recipient@example.com",
        key="new_draft_recipient"
    )
    
    subject = st.text_input(
        "Subject:",
        placeholder="Email subject",
        key="new_draft_subject"
    )
    
    instructions = st.text_area(
        "Instructions for AI:",
        placeholder="E.g., Write a professional email requesting a meeting next week...",
        height=100,
        key="new_draft_instructions"
    )
    
    context = st.text_area(
        "Additional Context (optional):",
        placeholder="Any additional information the AI should know...",
        height=80,
        key="new_draft_context"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🤖 Generate Draft", use_container_width=True):
            if not recipient or not subject or not instructions:
                st.error("Please fill in recipient, subject, and instructions.")
            else:
                generate_new_draft(
                    backend,
                    recipient=recipient,
                    subject=subject,
                    instructions=instructions,
                    context=context if context else None
                )
    
    with col2:
        if st.button("🔄 Clear Form", use_container_width=True):
            st.session_state.new_draft_recipient = ""
            st.session_state.new_draft_subject = ""
            st.session_state.new_draft_instructions = ""
            st.session_state.new_draft_context = ""
            st.rerun()
    
    # Show generated draft
    if st.session_state.get('current_draft'):
        display_draft(st.session_state.current_draft, backend, key_prefix="new")


def render_reply_draft_editor(backend, email_id: Optional[str] = None):
    """Render reply draft interface."""
    
    st.markdown("### Generate Reply Draft")
    
    # Email selection
    if not email_id:
        st.info("Select an email from the inbox to generate a reply.")
        return
    
    # Get email details
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    email = loop.run_until_complete(backend.get_email_by_id(email_id))
    loop.close()
    
    if not email:
        st.error("Email not found.")
        return
    
    st.markdown(f"**Replying to:** {email.subject}")
    st.caption(f"From: {email.sender}")
    
    additional_context = st.text_area(
        "Additional Context (optional):",
        placeholder="Any specific points to address or tone to use...",
        height=100,
        key="reply_draft_context"
    )
    
    if st.button("🤖 Generate Reply", use_container_width=True):
        generate_reply_draft(
            backend,
            email_id=email_id,
            additional_context=additional_context if additional_context else None
        )
    
    # Show generated draft
    if st.session_state.get('current_draft'):
        display_draft(st.session_state.current_draft, backend, key_prefix="reply")


def render_saved_drafts(backend):
    """Render saved drafts list."""
    
    st.markdown("### Saved Drafts")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        drafts = loop.run_until_complete(backend.get_all_drafts())
        loop.close()
        
        if not drafts:
            st.info("No saved drafts.")
            return
        
        for draft in drafts:
            render_saved_draft_card(draft, backend)
            
    except Exception as e:
        st.error(f"Error loading drafts: {str(e)}")


def render_saved_draft_card(draft: EmailDraft, backend):
    """Render individual saved draft card."""
    
    with st.expander(f"📧 {draft.subject}"):
        st.markdown(f"**To:** {draft.recipient}")
        st.caption(f"Created: {draft.created_at.strftime('%Y-%m-%d %H:%M')}")
        st.caption(f"Updated: {draft.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        st.markdown("**Body:**")
        st.text_area(
            "Draft body",
            value=draft.body,
            height=200,
            key=f"saved_draft_{draft.id}",
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 Export JSON", key=f"export_{draft.id}"):
                export_draft_json(draft)
        
        with col2:
            if st.button("✏️ Edit", key=f"edit_{draft.id}"):
                st.session_state.current_draft = draft
                st.rerun()
        
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{draft.id}"):
                delete_draft(backend, draft.id)


def display_draft(draft: EmailDraft, backend, key_prefix: str = "default"):
    """Display generated draft with editing options."""
    
    st.markdown("---")
    st.markdown("### Generated Draft")
    
    # Editable fields
    subject = st.text_input(
        "Subject:",
        value=draft.subject,
        key=f"{key_prefix}_draft_subject_edit"
    )
    
    body = st.text_area(
        "Body:",
        value=draft.body,
        height=300,
        key=f"{key_prefix}_draft_body_edit"
    )
    
    # Refinement
    refinement = st.text_input(
        "Refine draft (optional):",
        placeholder="E.g., Make it more formal, add a closing paragraph...",
        key=f"{key_prefix}_draft_refinement"
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refine", use_container_width=True, key=f"{key_prefix}_refine_btn"):
            if refinement:
                refine_draft(backend, draft.id, refinement)
    
    with col2:
        if st.button("💾 Save", use_container_width=True, key=f"{key_prefix}_save_btn"):
            save_draft_edits(backend, draft, subject, body)
    
    with col3:
        if st.button("📤 Export", use_container_width=True, key=f"{key_prefix}_export_btn"):
            export_draft_json(draft)
    
    with col4:
        if st.button("🗑️ Discard", use_container_width=True, key=f"{key_prefix}_discard_btn"):
            if 'current_draft' in st.session_state:
                del st.session_state.current_draft
            st.rerun()
    
    # Show metadata
    if draft.suggested_followups:
        with st.expander("💡 Suggested Follow-ups"):
            for followup in draft.suggested_followups:
                st.markdown(f"- {followup}")


def generate_new_draft(backend, recipient: str, subject: str, instructions: str, context: Optional[str]):
    """Generate new draft."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        draft = loop.run_until_complete(
            backend.generate_new_draft(
                recipient=recipient,
                subject=subject,
                instructions=instructions,
                context=context
            )
        )
        
        loop.close()
        
        st.session_state.current_draft = draft
        st.success("✅ Draft generated successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error generating draft: {str(e)}")


def generate_reply_draft(backend, email_id: str, additional_context: Optional[str]):
    """Generate reply draft."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        draft = loop.run_until_complete(
            backend.generate_reply_draft(
                email_id=email_id,
                additional_context=additional_context
            )
        )
        
        loop.close()
        
        st.session_state.current_draft = draft
        st.success("✅ Reply draft generated successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error generating reply: {str(e)}")


def refine_draft(backend, draft_id: str, refinement_instruction: str):
    """Refine existing draft."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        draft = loop.run_until_complete(
            backend.refine_draft(draft_id, refinement_instruction)
        )
        
        loop.close()
        
        st.session_state.current_draft = draft
        st.success("✅ Draft refined successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error refining draft: {str(e)}")


def save_draft_edits(backend, draft: EmailDraft, subject: str, body: str):
    """Save manual edits to draft."""
    try:
        draft.subject = subject
        draft.body = body
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(backend.db_service.save_draft(draft))
        loop.close()
        
        st.success("✅ Draft saved successfully!")
        
    except Exception as e:
        st.error(f"❌ Error saving draft: {str(e)}")


def delete_draft(backend, draft_id: str):
    """Delete draft."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(backend.delete_draft(draft_id))
        loop.close()
        
        st.success("✅ Draft deleted!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error deleting draft: {str(e)}")


def export_draft_json(draft: EmailDraft):
    """Export draft as JSON."""
    json_data = draft.to_json_metadata()
    json_str = json.dumps(json_data, indent=2)
    
    st.download_button(
        label="⬇️ Download JSON",
        data=json_str,
        file_name=f"draft_{draft.id}.json",
        mime="application/json"
    )
