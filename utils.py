"""
Utility functions for the chatbot application.
"""

import uuid
import streamlit as st

# Try to import get_script_run_ctx from different possible locations
# based on Streamlit version
try:
    # For newer Streamlit versions
    from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
except ImportError:
    try:
        # For older Streamlit versions
        from streamlit.script_run_context import get_script_run_ctx
    except ImportError:
        # Fallback if neither import works
        def get_script_run_ctx():
            return None

def get_session_id():
    """
    Get the current session ID from Streamlit session state.
    Creates a new ID if one doesn't exist.
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def get_user_id():
    """
    Get the current user ID from Streamlit session state.
    Creates a new ID if one doesn't exist.
    """
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def get_streamlit_session_id():
    """
    Get the Streamlit session ID from the script run context.
    This is different from our application session ID.
    Falls back to a generated UUID if the context is not available.
    """
    ctx = get_script_run_ctx()
    if ctx is not None:
        return ctx.session_id
    return str(uuid.uuid4())  # Fallback to a generated UUID

def format_source_documents(source_documents):
    """
    Format source documents for display in Streamlit.
    """
    if not source_documents:
        return None
        
    formatted_docs = []
    for i, doc in enumerate(source_documents):
        if hasattr(doc, 'metadata') and doc.metadata:
            source = doc.metadata.get('source', 'Unknown')
            formatted_docs.append(f"Source {i+1}: {source}")
    
    return "\n".join(formatted_docs) if formatted_docs else None

def write_message(role, content, save=True):
    """
    Helper function to write a message to the Streamlit UI and optionally save to session state.
    
    Args:
        role (str): The role of the message sender (e.g., "user", "assistant", "system")
        content (str): The content of the message
        save (bool): Whether to save the message to session state
    """
    # Append to session state if save is True
    if save and "messages" in st.session_state:
        st.session_state.messages.append({"role": role, "content": content})
    
    # Write to UI
    with st.chat_message(role):
        st.markdown(content)
