# Import necessary library
import streamlit as st

class SessionState(object):
    """Store session state across app reruns."""
    
    def __init__(self, **kwargs):
        """
        Initialize the SessionState object with provided key-value pairs.

        Args:
            **kwargs: Arbitrary keyword arguments to initialize session state variables.
        """
        for key, val in kwargs.items():
            setattr(self, key, val)

def get_state(**kwargs):
    """
    Get session state, creating it if necessary.

    Args:
        **kwargs: Arbitrary keyword arguments for initializing SessionState.

    Returns:
        SessionState: The session state object.
    """
    if 'session_state' not in st.session_state:
        st.session_state['session_state'] = SessionState(**kwargs)
    return st.session_state['session_state']
