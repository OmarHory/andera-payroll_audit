import streamlit as st
import re

def render_markdown(text):
    """
    A very simple text renderer that preserves all formatting and ensures text is visible.
    Uses Streamlit's built-in text display rather than markdown to avoid parsing issues.
    """
    if text is None or text == "":
        return st.info("No content available")
    
    # Most straightforward approach: just show the text as-is in a text box
    # This will preserve all formatting including parentheses and plus signs
    st.code(text, language=None)  # Using code display with no syntax highlighting ensures text is visible
    
    return True


def render_simple_text(text):
    """
    Render plain text without markdown parsing to avoid formatting issues
    """
    if text is None or text == "":
        return st.info("No content available")
    
    st.text_area("", value=text, height=200, disabled=True, label_visibility="collapsed")
    return True

def render_code_block(code, language="python"):
    """
    Render a code block with syntax highlighting
    """
    st.code(code, language=language)
    
def render_report_section(title, content):
    """
    Render a section of a report with proper formatting
    """
    st.markdown(f"### {title}")
    render_markdown(content)
