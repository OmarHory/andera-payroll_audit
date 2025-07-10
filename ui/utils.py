import os
import uuid
from pathlib import Path
from ui.logger import logger


def create_uuid_folder():
    folder_uuid = str(uuid.uuid4())
    folder_path = Path("data") / folder_uuid
    folder_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Created new UUID folder: {folder_uuid} at {folder_path}")
    return folder_uuid, str(folder_path)


def save_uploaded_file(uploaded_file, save_path: str):
    file_path = Path(save_path) / uploaded_file.name
    file_size = uploaded_file.size
    logger.info(f"💾 Saving file: {uploaded_file.name} ({file_size} bytes) to {save_path}")
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    logger.info(f"✅ Successfully saved file: {uploaded_file.name}")
    return str(file_path)


def format_execution_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {secs:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"


def setup_data_directory():
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(exist_ok=True)
    return data_dir


def format_markdown(text):
    """
    Format text to render properly as markdown in Streamlit.
    Ensures special characters and spacing are preserved correctly.
    """
    if text is None:
        return "No content available"
    
    # Replace problematic sequences that might be causing rendering issues
    # Ensure spaces around parentheses and special characters are preserved
    formatted_text = text.replace("(", " (")
    formatted_text = formatted_text.replace("+", " + ")
    
    # Fix common markdown rendering issues
    formatted_text = formatted_text.replace("  ", " ")
    
    return formatted_text