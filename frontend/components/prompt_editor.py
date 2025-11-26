"""Prompt configuration editor component."""
import streamlit as st
from datetime import datetime

from backend.models.prompt import PromptConfig
from backend.config.settings import settings


def render_prompt_editor(backend):
    """Render prompt brain configuration panel."""
    
    st.subheader("🧠 Prompt Brain Configuration")
    
    st.info(
        "Configure the prompts that guide the AI agents. "
        "These prompts control how emails are categorized, "
        "action items are extracted, and replies are drafted."
    )
    
    # Get current active prompts
    active_prompts = st.session_state.get('active_prompts', {})
    
    # Tabs for different prompt types
    tab1, tab2, tab3 = st.tabs([
        "📂 Categorization",
        "✅ Action Items",
        "✉️ Reply Drafts"
    ])
    
    # Categorization Prompt
    with tab1:
        render_prompt_section(
            backend=backend,
            prompt_type="categorization",
            prompt_name="Categorization Prompt",
            default_prompt=settings.default_category_prompt,
            current_prompt=active_prompts.get('categorization'),
            description="This prompt guides how emails are categorized into URGENT, ACTION_REQUIRED, INFORMATIONAL, or SPAM."
        )
    
    # Action Item Prompt
    with tab2:
        render_prompt_section(
            backend=backend,
            prompt_type="action_item",
            prompt_name="Action Item Extraction Prompt",
            default_prompt=settings.default_action_prompt,
            current_prompt=active_prompts.get('action_item'),
            description="This prompt guides how action items are extracted from emails."
        )
    
    # Reply Draft Prompt
    with tab3:
        render_prompt_section(
            backend=backend,
            prompt_type="reply_draft",
            prompt_name="Reply Draft Prompt",
            default_prompt=settings.default_reply_prompt,
            current_prompt=active_prompts.get('reply_draft'),
            description="This prompt guides the tone and style of auto-generated reply drafts."
        )


def render_prompt_section(
    backend,
    prompt_type: str,
    prompt_name: str,
    default_prompt: str,
    current_prompt,
    description: str
):
    """Render individual prompt editing section."""
    
    st.markdown(f"### {prompt_name}")
    st.caption(description)
    
    # Display current prompt or default
    current_text = (
        current_prompt.prompt_text if current_prompt
        else default_prompt
    )
    
    # Text area for editing
    new_prompt_text = st.text_area(
        f"Edit {prompt_name}",
        value=current_text,
        height=200,
        key=f"prompt_editor_{prompt_type}",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            f"💾 Save {prompt_name}",
            key=f"save_prompt_{prompt_type}",
            use_container_width=True
        ):
            save_prompt(
                backend,
                prompt_type=prompt_type,
                prompt_name=prompt_name,
                prompt_text=new_prompt_text
            )
    
    with col2:
        if st.button(
            "🔄 Reset to Default",
            key=f"reset_prompt_{prompt_type}",
            use_container_width=True
        ):
            st.session_state[f"prompt_editor_{prompt_type}"] = default_prompt
            st.rerun()
    
    # Show prompt history
    with st.expander("📜 Prompt History"):
        st.caption("Previous versions of this prompt will appear here.")
        # TODO: Implement prompt version history


def save_prompt(backend, prompt_type: str, prompt_name: str, prompt_text: str):
    """Save prompt configuration."""
    try:
        import asyncio
        
        # Create prompt config
        prompt_config = PromptConfig(
            name=prompt_name,
            prompt_type=prompt_type,
            prompt_text=prompt_text,
            is_active=True
        )
        
        # Save using backend
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        prompt_id = loop.run_until_complete(
            backend.save_prompt_config(prompt_config)
        )
        loop.close()
        
        st.success(f"✅ {prompt_name} saved successfully!")
        
        # Refresh active prompts in session state
        refresh_active_prompts(backend)
        
    except Exception as e:
        st.error(f"❌ Error saving prompt: {str(e)}")


def refresh_active_prompts(backend):
    """Refresh active prompts in session state."""
    try:
        import asyncio
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        active_prompts = loop.run_until_complete(backend.get_active_prompts())
        loop.close()
        
        st.session_state['active_prompts'] = active_prompts
        
    except Exception as e:
        st.error(f"Error refreshing prompts: {str(e)}")
