"""
Utility functions for the Gradio-based chatbot application.
"""

import uuid

# Global state for session and user IDs
_session_id = None
_user_id = None

def get_session_id():
    """
    Get the current session ID.
    Creates a new ID if one doesn't exist.
    """
    global _session_id
    if _session_id is None:
        _session_id = str(uuid.uuid4())
    return _session_id

def get_user_id():
    """
    Get the current user ID.
    Creates a new ID if one doesn't exist.
    """
    global _user_id
    if _user_id is None:
        _user_id = str(uuid.uuid4())
    return _user_id

def reset_ids():
    """
    Reset both session and user IDs.
    Useful for testing or when starting a new session.
    """
    global _session_id, _user_id
    _session_id = None
    _user_id = None

def format_source_documents(source_documents):
    """
    Format source documents for display.
    """
    if not source_documents:
        return None
        
    formatted_docs = []
    for i, doc in enumerate(source_documents):
        if hasattr(doc, 'metadata') and doc.metadata:
            source = doc.metadata.get('source', 'Unknown')
            formatted_docs.append(f"Source {i+1}: {source}")
    
    return "\n".join(formatted_docs) if formatted_docs else None
