# functions/page_utils.py
import streamlit as st
import os

def get_current_page_name():
    """
    Tenta identificar o nome da página atual através do contexto de execução.
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx is None:
            return None
        return os.path.basename(ctx.script_path)
    except:
        return st.session_state.get("current_page", None)
