import streamlit as st
import os
import uuid
import shutil
from pathlib import Path
from typing import List
import time
import json
import logging
from datetime import datetime

# Import the invoke function from our app
from app.graph import invoke

# Configure streamlit-specific logger
def setup_streamlit_logger():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create logger for streamlit
    logger = logging.getLogger("streamlit_app")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(f"logs/streamlit_app_{timestamp}.log", encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter with emojis
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_streamlit_logger()

# Page configuration
st.set_page_config(
    page_title="🧾 Junior Payroll Auditor",
    page_icon="🧾",
    layout="wide"
)

# Custom CSS for hackathon styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Force remove default Streamlit background */
    .stApp, .stApp > div, .main, .block-container {
        background: transparent !important;
    }
    
    /* Global Styles */
    .main > div {
        padding-top: 2rem;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }
    
    /* Enhanced animated background with fallback */
    .stApp {
        background: #667eea !important; /* Fallback solid color */
        background: linear-gradient(-45deg, #667eea, #764ba2, #667eea, #f093fb, #764ba2) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 8s ease infinite !important;
        min-height: 100vh !important;
        position: relative !important;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(-45deg, 
            #667eea, 
            #764ba2, 
            #667eea, 
            #f093fb, 
            #764ba2);
        background-size: 400% 400%;
        animation: gradientBG 8s ease infinite;
        z-index: -2;
        pointer-events: none;
    }
    
    /* Secondary background layer for extra visibility */
    body {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 8s ease infinite !important;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 50%; }
        50% { background-position: 0% 100%; }
        75% { background-position: 100% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Main content overlay */
    .main > div > div {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        z-index: 1;
    }
    
    /* Force background visibility */
    .stApp > .main {
        background: transparent !important;
    }
    
    .stApp > .main > div {
        background: transparent !important;
    }
    
    /* Add floating particles effect */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
        animation: particles 20s linear infinite;
        z-index: -1;
        pointer-events: none;
    }
    
    @keyframes particles {
        0% { transform: translateY(0px) rotate(0deg); }
        100% { transform: translateY(-100px) rotate(360deg); }
    }
    
    /* Header section with background */
    .header-section {
        background: linear-gradient(135deg, rgba(74, 85, 104, 0.95), rgba(102, 126, 234, 0.95));
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 3rem 2rem;
        margin: 2rem 0;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .header-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 4s infinite;
    }
    
    /* Header styling */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    /* Status bar */
    .status-bar {
        background: linear-gradient(135deg, #4a5568, #667eea);
        padding: 1rem 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        color: white;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 15px 35px rgba(74, 85, 104, 0.3);
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Card sections */
    .upload-section {
        background: linear-gradient(135deg, #4a5568 0%, #667eea 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(74, 85, 104, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .upload-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        100% { transform: translateX(100%); }
    }
    
    .upload-section h3 {
        color: white;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .task-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .task-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite 1s;
    }
    
    .task-section h3 {
        color: white;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .execution-section {
        background: linear-gradient(135deg, #38b2ac 0%, #4299e1 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(56, 178, 172, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .execution-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite 2s;
    }
    
    .execution-section h3 {
        color: white;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .results-section {
        background: linear-gradient(135deg, #ed8936 0%, #f6ad55 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(237, 137, 54, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .results-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite 1.5s;
    }
    
    .results-section h3 {
        color: white;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4a5568, #667eea);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 25px rgba(74, 85, 104, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 20px 40px rgba(74, 85, 104, 0.5);
        background: linear-gradient(135deg, #667eea, #38b2ac);
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(1.02);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.4);
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.6);
        transform: scale(1.02);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(255, 255, 255, 0.6);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.7);
    }
    
    /* Metrics styling */
    .metric-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #4a5568, #667eea, #38b2ac, #4299e1);
        background-size: 200% 100%;
        animation: progressShine 2s linear infinite;
    }
    
    @keyframes progressShine {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #38b2ac, #4299e1);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
    }
    
    .stError {
        background: linear-gradient(135deg, #e53e3e, #fc8181);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ed8936, #f6ad55);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
    }
    
    /* Floating animation for elements */
    .floating {
        animation: floating 6s ease-in-out infinite;
    }
    
    @keyframes floating {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'execution_results' not in st.session_state:
    st.session_state.execution_results = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'current_uuid' not in st.session_state:
    st.session_state.current_uuid = None
if 'execution_in_progress' not in st.session_state:
    st.session_state.execution_in_progress = False

def create_uuid_folder() -> str:
    """Create a UUID-based folder in the data directory"""
    folder_uuid = str(uuid.uuid4())
    folder_path = Path("data") / folder_uuid
    folder_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Created new UUID folder: {folder_uuid} at {folder_path}")
    return folder_uuid, str(folder_path)

def save_uploaded_file(uploaded_file, save_path: str):
    """Save uploaded file to the specified path"""
    file_path = Path(save_path) / uploaded_file.name
    file_size = uploaded_file.size
    logger.info(f"💾 Saving file: {uploaded_file.name} ({file_size} bytes) to {save_path}")
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    logger.info(f"✅ Successfully saved file: {uploaded_file.name}")
    return str(file_path)

def format_execution_time(seconds: float) -> str:
    """Format execution time in a human-readable format"""
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

# Main UI
def main():
    # Log app startup
    if 'app_started' not in st.session_state:
        logger.info("🚀 Junior Payroll Auditor Streamlit App Started")
        logger.info(f"⏰ Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.session_state.app_started = True
    
    # Header with background
    st.markdown('''
    <div class="header-section floating">
        <h1 class="main-header">🧾 Junior Payroll Auditor</h1>
        <p class="subtitle">AI-Powered Payroll Analysis & Auditing System 🚀</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Check data directory
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(exist_ok=True)
    
    # Reset button in a floating container
    col_reset1, col_reset2, col_reset3 = st.columns([2, 1, 2])
    with col_reset2:
        if st.button("🔄 Reset Session", use_container_width=True):
            logger.info("🔄 User requested session reset")
            if st.session_state.current_uuid:
                logger.info(f"🗑️ Clearing session: {st.session_state.current_uuid}")
            st.session_state.clear()
            logger.info("✅ Session reset completed")
            st.rerun()

    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # File Upload Section
        st.markdown("""
        <div class="upload-section floating">
            <h3>🌟 File Upload Portal</h3>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "🔥 Drop Your Documents Here",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'xlsx', 'csv', 'png', 'jpg', 'jpeg'],
            help="💫 Upload payroll documents, timesheets, spreadsheets, or any audit-related files. Multiple formats supported!"
        )
        
        if uploaded_files and not st.session_state.execution_in_progress:
            logger.info(f"📄 User selected {len(uploaded_files)} files for upload")
            for file in uploaded_files:
                logger.info(f"   📋 Selected: {file.name} ({file.size} bytes, type: {file.type})")
            
            if st.button("✨ Lock & Load Files", type="primary"):
                logger.info("💾 User clicked Save Files button")
                with st.spinner("Saving files..."):
                    # Create UUID folder
                    folder_uuid, folder_path = create_uuid_folder()
                    st.session_state.current_uuid = folder_uuid
                    logger.info(f"🆔 New session UUID: {folder_uuid}")
                    
                    # Save all files
                    saved_files = []
                    total_size = 0
                    for uploaded_file in uploaded_files:
                        file_path = save_uploaded_file(uploaded_file, folder_path)
                        saved_files.append({
                            "name": uploaded_file.name,
                            "size": uploaded_file.size,
                            "path": file_path
                        })
                        total_size += uploaded_file.size
                    
                    st.session_state.uploaded_files = saved_files
                    
                    logger.info(f"📊 File upload summary:")
                    logger.info(f"   📁 Session: {folder_uuid}")
                    logger.info(f"   📄 Files saved: {len(saved_files)}")
                    logger.info(f"   💾 Total size: {total_size} bytes")
                    
                    st.success(f"🎉 {len(saved_files)} files successfully locked & loaded! Session: `{folder_uuid[:8]}...`")
                    
                    # Show saved files
                    st.markdown("**Saved Files:**")
                    for file_info in saved_files:
                        st.markdown(f"- 📄 {file_info['name']} ({file_info['size']} bytes)")
    
    with col2:
        # Tasks Input Section
        st.markdown("""
        <div class="task-section floating">
            <h3>✨ Custom Audit Tasks</h3>
        </div>
        """, unsafe_allow_html=True)
        
        logger.info("✏️ User is creating custom audit tasks")
        
        tasks_input = st.text_area(
            "🎯 Define Your Audit Mission",
            value="",
            height=250,
            placeholder="🚀 Enter your audit tasks here (one per line):\n\n💡 Examples:\n• Check for payroll discrepancies and irregularities\n• Verify employee overtime calculations\n• Audit tax withholdings and deductions\n• Review salary and wage accuracy\n• Validate benefits calculations\n• Ensure labor law compliance\n• Analyze payroll cost trends",
            disabled=st.session_state.execution_in_progress,
            help="Each line will be treated as a separate audit task. Be specific for better results!"
        )
    
    # Execution Section
    st.markdown("""
    <div class="execution-section floating">
        <h3>🚀 AI Execution Command Center</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Show execution button and status
    execution_col1, execution_col2, execution_col3 = st.columns([1, 2, 1])
    
    with execution_col2:
        if st.session_state.uploaded_files and tasks_input.strip():
            if not st.session_state.execution_in_progress:
                if st.button("🎯 LAUNCH AI AUDIT", type="primary", use_container_width=True):
                    # Parse tasks
                    tasks = [task.strip() for task in tasks_input.split('\n') if task.strip()]
                    
                    logger.info("🚀 User initiated audit execution")
                    logger.info(f"📝 Parsed {len(tasks)} tasks from input")
                    for i, task in enumerate(tasks, 1):
                        logger.info(f"   {i}. 🎯 {task}")
                    
                    if tasks:
                        st.session_state.execution_in_progress = True
                        logger.info("⚡ Execution started - setting progress flag")
                        
                        # Execution with progress tracking
                        with st.spinner("🔄 Executing audit... This may take a few minutes"):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Update progress
                            progress_bar.progress(20)
                            status_text.text("🔍 Analyzing uploaded files...")
                            logger.info("🔍 Progress: 20% - Starting file analysis")
                            
                            start_time = time.time()
                            
                            # Get data path
                            data_path = str(Path("data") / st.session_state.current_uuid)
                            logger.info(f"📁 Execution data path: {data_path}")
                            
                            # Execute the audit
                            try:
                                progress_bar.progress(40)
                                status_text.text("🧠 Processing with AI...")
                                logger.info("🧠 Progress: 40% - Starting AI processing")
                                
                                logger.info("🎬 Calling invoke function with parameters:")
                                logger.info(f"   🆔 Thread ID: {st.session_state.current_uuid}")
                                logger.info(f"   📁 Data path: {data_path}")
                                logger.info(f"   📝 Tasks count: {len(tasks)}")
                                
                                result = invoke(
                                    thread_id=st.session_state.current_uuid,
                                    data_path=data_path,
                                    tasks=tasks
                                )
                                
                                progress_bar.progress(100)
                                execution_time = time.time() - start_time
                                logger.info(f"⏱️ Streamlit execution completed in {execution_time:.2f} seconds")
                                
                                st.session_state.execution_results = {
                                    **result,
                                    "execution_time": execution_time,
                                    "timestamp": time.time()
                                }
                                
                                if result.get("success", False):
                                    logger.info("✅ Audit execution successful!")
                                    logger.info(f"📊 Documents processed: {result.get('documents_processed', 0)}")
                                    logger.info(f"🎯 Tasks completed: {result.get('tasks_count', 0)}")
                                else:
                                    logger.error(f"❌ Audit execution failed: {result.get('error', 'Unknown error')}")
                                
                                status_text.text("✅ Audit completed successfully!")
                                time.sleep(1)
                                
                            except Exception as e:
                                execution_time = time.time() - start_time
                                logger.error(f"💥 Streamlit execution error after {execution_time:.2f}s: {str(e)}")
                                st.error(f"❌ Error during execution: {str(e)}")
                                result = {
                                    "success": False,
                                    "error": str(e),
                                    "execution_time": execution_time
                                }
                                st.session_state.execution_results = result
                            
                            finally:
                                st.session_state.execution_in_progress = False
                                logger.info("🏁 Execution completed - clearing progress flag")
                                st.rerun()
            else:
                st.info("🚀 AI audit in progress... Intelligence analysis underway!")
        else:
            if not st.session_state.uploaded_files:
                st.warning("🌟 Ready to upload? Drop your files in the portal above!")
            if not tasks_input.strip():
                st.warning("✨ Define your audit mission to begin the intelligence analysis!")

    # Results Section
    if st.session_state.execution_results:
        logger.info("📊 Displaying audit results to user")
        results = st.session_state.execution_results
        logger.info(f"📋 Results summary: Success={results.get('success', False)}, "
                   f"Tasks={results.get('tasks_count', 0)}, "
                   f"Docs={results.get('documents_processed', 0)}")
        
        st.markdown("""
        <div class="results-section floating">
            <h3>🎉 Audit Intelligence Report</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics row
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            status_icon = "✅" if results.get("success", False) else "❌"
            st.metric("Status", f"{status_icon} {'Success' if results.get('success', False) else 'Failed'}")
        
        with metric_col2:
            exec_time = results.get("execution_time", 0)
            st.metric("Execution Time", format_execution_time(exec_time))
        
        with metric_col3:
            docs_processed = results.get("documents_processed", 0)
            st.metric("Documents Processed", docs_processed)
        
        with metric_col4:
            tasks_count = results.get("tasks_count", 0)
            st.metric("Tasks Executed", tasks_count)
        
        if results.get("success", False):
            # Main Report
            st.markdown("### 📋 Final Report")
            st.markdown(results.get("report", "No report available"))
            
            # Detailed Execution Results
            if results.get("execution_details"):
                st.markdown("### 🔍 Detailed Task Results")
                
                for i, detail in enumerate(results["execution_details"], 1):
                    with st.expander(f"Task {i}: {detail['task']}", expanded=i==1):
                        status_color = "green" if detail['status'] == "PASS" else "red"
                        st.markdown(f"**Status:** :{status_color}[{detail['status']}]")
                        st.markdown(f"**Output:**")
                        st.write(detail['output'])
            
            # Raw Results (for debugging)
            with st.expander("🔧 Raw Results (Debug)", expanded=False):
                st.json(results)
        
        else:
            st.error(f"❌ Execution failed: {results.get('error', 'Unknown error')}")
        
        # Download results button
        if st.button("📊 Export Intelligence Report"):
            logger.info("💾 User requested results download")
            results_json = json.dumps(results, indent=2, default=str)
            filename = f"audit_results_{st.session_state.current_uuid[:8]}.json"
            logger.info(f"📄 Preparing download: {filename} ({len(results_json)} chars)")
            
            st.download_button(
                label="⬇️ Download JSON Report",
                data=results_json,
                file_name=filename,
                mime="application/json"
            )

if __name__ == "__main__":
    logger.info("🎬 Starting Streamlit app main function")
    main()
    logger.info("🏁 Streamlit app main function completed") 