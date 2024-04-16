import streamlit as st

class SessionState(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def get_state(**kwargs):
    if 'session_state' not in st.session_state:
        st.session_state['session_state'] = SessionState(**kwargs)
    return st.session_state['session_state']
