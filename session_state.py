# Import necessary library
import streamlit as st

class SessionState(object):
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
    Get the session state and initialize if not already created.

    Args:
        **kwargs: Arbitrary keyword arguments to initialize session state variables if session state is not present.

    Returns:
        SessionState: The session state object.
    """
    if 'session_state' not in st.session_state:
        st.session_state['session_state'] = SessionState(**kwargs)
    return st.session_state['session_state']
