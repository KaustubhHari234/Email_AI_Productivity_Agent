"""Main Streamlit application for Email Productivity Agent."""
import streamlit as st
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.main import EmailProductivityBackend
from backend.models.email import EmailCategory
from frontend.components.email_list import render_email_list, render_email_details
from frontend.components.prompt_editor import render_prompt_editor
from frontend.components.agent_chat import render_agent_chat
from frontend.components.draft_editor import render_draft_editor


# Page configuration
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_custom_css():
    """Load custom CSS styles."""
    # Load external CSS file
    css_file = Path(__file__).parent / "styles" / "custom.css"
    if css_file.exists():
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom CSS file not found")


# Initialize backend
@st.cache_resource
def get_backend():
    """Initialize and cache backend instance."""
    return EmailProductivityBackend()


def initialize_session_state():
    """Initialize session state variables."""
    if 'emails_loaded' not in st.session_state:
        st.session_state.emails_loaded = False
    
    if 'emails' not in st.session_state:
        st.session_state.emails = []
    
    if 'selected_email_id' not in st.session_state:
        st.session_state.selected_email_id = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'active_prompts' not in st.session_state:
        st.session_state.active_prompts = {}
    
    if 'current_draft' not in st.session_state:
        st.session_state.current_draft = None


def render_sidebar(backend):
    """Render sidebar with controls."""
    st.sidebar.title("📧 Email Agent Control")
    
    st.sidebar.markdown("---")
    
    # Phase 1: Email Loading
    st.sidebar.subheader("📥 Load Emails")
    
    email_source = st.sidebar.selectbox(
        "Email Source",
        options=["Mock Inbox", "Gmail (Coming Soon)", "Outlook (Coming Soon)"],
        index=0
    )
    
    if st.sidebar.button("📂 Load Emails", use_container_width=True):
        load_emails(backend)
    
    st.sidebar.markdown("---")
    
    # Statistics
    if st.session_state.emails_loaded:
        st.sidebar.subheader("📊 Inbox Statistics")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            stats = loop.run_until_complete(backend.get_category_statistics())
            loop.close()
            
            total = sum(stats.values())
            st.sidebar.metric("Total Emails", total)
            
            for category, count in stats.items():
                if count > 0:
                    st.sidebar.metric(category, count)
        except Exception as e:
            st.sidebar.error(f"Error loading stats: {str(e)}")
    
    st.sidebar.markdown("---")
    
    # Quick Actions
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        refresh_data(backend)
    
    if st.sidebar.button("🗑️ Clear Cache", use_container_width=True):
        st.cache_resource.clear()
        st.success("Cache cleared!")
    
    st.sidebar.markdown("---")
    
    # About
    with st.sidebar.expander("ℹ️ About"):
        st.markdown("""
        **Email Productivity Agent**
        
        Version: 0.1.0
        
        Technologies:
        - Streamlit
        - Google Gemini
        - Pinecone
        - MongoDB
        
        Built with UV package manager
        """)


def load_emails(backend):
    """Load and process emails."""
    with st.spinner("Loading and processing emails..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            emails = loop.run_until_complete(
                backend.load_and_process_emails(source="mock")
            )
            
            loop.close()
            
            st.session_state.emails = emails
            st.session_state.emails_loaded = True
            
            st.success(f"✅ Successfully loaded and processed {len(emails)} emails!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error loading emails: {str(e)}")


def refresh_data(backend):
    """Refresh email data from database."""
    with st.spinner("Refreshing data..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            emails = loop.run_until_complete(backend.get_emails())
            active_prompts = loop.run_until_complete(backend.get_active_prompts())
            
            loop.close()
            
            st.session_state.emails = emails
            st.session_state.active_prompts = active_prompts
            st.session_state.emails_loaded = len(emails) > 0
            
            st.success("✅ Data refreshed!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error refreshing data: {str(e)}")


def on_email_select(email_id: str):
    """Callback for email selection."""
    st.session_state.selected_email_id = email_id


def render_main_content(backend):
    """Render main content area."""
    
    # Title
    st.title("📧 Email Productivity Agent")
    st.caption("Intelligent prompt-driven email management with AI agents")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📬 Inbox",
        "🧠 Prompt Brain",
        "💬 Agent Chat",
        "✉️ Drafts"
    ])
    
    # Tab 1: Inbox (Phase 1)
    with tab1:
        render_inbox_tab(backend)
    
    # Tab 2: Prompt Brain (Phase 1)
    with tab2:
        render_prompt_editor(backend)
    
    # Tab 3: Agent Chat (Phase 2)
    with tab3:
        render_agent_chat(backend)
    
    # Tab 4: Drafts (Phase 3)
    with tab4:
        render_draft_editor(backend, st.session_state.selected_email_id)


def render_inbox_tab(backend):
    """Render inbox tab content."""
    
    if not st.session_state.emails_loaded:
        st.info("👈 Load emails from the sidebar to get started!")
        
        # Show example
        with st.expander("💡 What you can do"):
            st.markdown("""
            **Phase 1: Email Ingestion & Knowledge Base**
            - Load emails from mock inbox
            - View categorized emails
            - Configure AI prompts for categorization
            
            **Phase 2: Email Processing Agent (RAG)**
            - Ask questions about your inbox
            - Get summaries and insights
            - Find urgent or specific emails
            
            **Phase 3: Draft Generation**
            - Auto-generate reply drafts
            - Create new emails with AI
            - Edit and refine drafts
            """)
        return
    
    # Two-column layout
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        render_email_list(
            emails=st.session_state.emails,
            on_select_callback=on_email_select,
            selected_email_id=st.session_state.selected_email_id
        )
    
    with col2:
        if st.session_state.selected_email_id:
            # Get selected email
            selected_email = next(
                (e for e in st.session_state.emails 
                 if e.id == st.session_state.selected_email_id),
                None
            )
            
            if selected_email:
                render_email_details(selected_email)
                
                st.markdown("---")
                
                # Action buttons
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("📝 Generate Reply", use_container_width=True):
                        st.session_state.active_tab = "Drafts"
                        st.rerun()
                
                with col_b:
                    if st.button("💬 Ask About Email", use_container_width=True):
                        st.session_state.active_tab = "Agent Chat"
                        st.rerun()
                
                with col_c:
                    if st.button("📊 Summarize", use_container_width=True):
                        summarize_email(backend, selected_email.id)
            else:
                st.info("Email not found")
        else:
            st.info("👈 Select an email from the list to view details")


def summarize_email(backend, email_id: str):
    """Summarize selected email."""
    with st.spinner("Generating summary..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            summary = loop.run_until_complete(
                backend.summarize_email(email_id)
            )
            
            loop.close()
            
            st.info(f"📝 **Summary:** {summary}")
            
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")


def main():
    """Main application entry point."""
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Get backend instance
    backend = get_backend()
    
    # Render sidebar
    render_sidebar(backend)
    
    # Render main content
    render_main_content(backend)
    
    # Footer
    st.markdown("---")
    st.caption("Email Productivity Agent v0.1.0 | Built with Streamlit, Gemini, Pinecone & MongoDB")


if __name__ == "__main__":
    main()
