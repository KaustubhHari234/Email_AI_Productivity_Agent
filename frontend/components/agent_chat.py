"""Agent chat interface component."""
import streamlit as st
from typing import List, Dict
import asyncio


def render_agent_chat(backend):
    """Render chat interface for email agent."""
    
    st.subheader("💬 Email Agent Chat")
    
    st.info(
        "Ask questions about your inbox, request summaries, find specific emails, "
        "or get help with drafting responses."
    )
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Quick action buttons
    st.markdown("**Quick Actions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Summarize Inbox", use_container_width=True):
            process_quick_action(backend, "summarize_inbox")
    
    with col2:
        if st.button("🔥 Find Urgent", use_container_width=True):
            process_quick_action(backend, "find_urgent")
    
    with col3:
        if st.button("✅ Show Tasks", use_container_width=True):
            process_quick_action(backend, "show_tasks")
    
    st.markdown("---")
    
    # Chat messages display
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            render_chat_message(message)
    
    # Chat input
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask a question...",
            placeholder="e.g., What tasks do I need to do today?",
            key="chat_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    if send_button and user_input:
        process_chat_message(backend, user_input)
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


def render_chat_message(message: Dict):
    """Render individual chat message."""
    
    role = message.get('role', 'user')
    content = message.get('content', '')
    sources = message.get('sources', [])
    
    if role == 'user':
        st.markdown(
            f"""
            <div class="chat-message user">
                <strong>You:</strong> {content}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="chat-message agent">
                <strong>Agent:</strong> {content}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Show sources if available
        if sources:
            with st.expander("📎 Sources"):
                for idx, source in enumerate(sources, 1):
                    metadata = source.get('metadata', {})
                    st.caption(
                        f"{idx}. **{metadata.get('subject', 'N/A')}** "
                        f"from {metadata.get('sender', 'N/A')} "
                        f"(Score: {source.get('score', 0):.2f})"
                    )


def process_chat_message(backend, user_input: str):
    """Process user chat message."""
    
    # Add user message to history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input
    })
    
    try:
        # Process with backend
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(
            backend.query_inbox(user_input)
        )
        
        loop.close()
        
        # Add agent response to history
        st.session_state.chat_history.append({
            'role': 'agent',
            'content': response.get('answer', 'No response'),
            'sources': response.get('sources', [])
        })
        
    except Exception as e:
        st.session_state.chat_history.append({
            'role': 'agent',
            'content': f"Error: {str(e)}",
            'sources': []
        })


def process_quick_action(backend, action_type: str):
    """Process quick action button."""
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if action_type == "summarize_inbox":
            response = loop.run_until_complete(backend.get_inbox_summary())
            user_message = "Summarize my inbox"
        elif action_type == "find_urgent":
            response = loop.run_until_complete(backend.find_urgent_emails())
            user_message = "Show me urgent emails"
        elif action_type == "show_tasks":
            action_items = loop.run_until_complete(backend.get_all_action_items())
            response = format_action_items(action_items)
            user_message = "Show me all tasks"
        else:
            response = "Unknown action"
            user_message = action_type
        
        loop.close()
        
        # Add to chat history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_message
        })
        
        st.session_state.chat_history.append({
            'role': 'agent',
            'content': response,
            'sources': []
        })
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing action: {str(e)}")


def format_action_items(action_items: List[Dict]) -> str:
    """Format action items for display."""
    
    if not action_items:
        return "No pending action items found."
    
    response_lines = [f"Found {len(action_items)} action items:\n"]
    
    for item in action_items[:10]:  # Limit to 10
        action = item.get('action_item', {})
        email_subject = item.get('email_subject', 'N/A')
        
        response_lines.append(
            f"• {action.get('description', 'N/A')} "
            f"[{action.get('priority', 'Medium')}] "
            f"from email: {email_subject}"
        )
    
    return "\n".join(response_lines)
