import streamlit as st
import time
from datetime import datetime
import sys
import os

# Ensure current directory is in Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from service.graph import invoke
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.error("Please ensure the service module is properly installed")
    st.stop()

from ui.logger import logger
from ui.styles import STREAMLIT_CSS
from ui.components import (
    render_header, 
    render_reset_button, 
    render_file_upload, 
    render_tasks_input,
    render_execution_section,
    render_execution_results
)
from ui.utils import create_uuid_folder, save_uploaded_file, setup_data_directory


def initialize_session_state():
    if 'execution_results' not in st.session_state:
        st.session_state.execution_results = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'current_uuid' not in st.session_state:
        st.session_state.current_uuid = None
    if 'execution_in_progress' not in st.session_state:
        st.session_state.execution_in_progress = False


def configure_page():
    st.set_page_config(
        page_title="🧾 Junior Payroll Auditor",
        page_icon="🧾",
        layout="wide"
    )
    st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)


def log_app_startup():
    if 'app_started' not in st.session_state:
        logger.info("🚀 Junior Payroll Auditor Streamlit App Started")
        logger.info(f"⏰ Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.session_state.app_started = True


def handle_file_upload(uploaded_files):
    if uploaded_files and not st.session_state.execution_in_progress:
        logger.info(f"📄 User selected {len(uploaded_files)} files for upload")
        for file in uploaded_files:
            logger.info(f"   📋 Selected: {file.name} ({file.size} bytes, type: {file.type})")
        
        if st.button("✨ Lock & Load Files", type="primary"):
            logger.info("💾 User clicked Save Files button")
            with st.spinner("Saving files..."):
                folder_uuid, folder_path = create_uuid_folder()
                st.session_state.current_uuid = folder_uuid
                logger.info(f"🆔 New session UUID: {folder_uuid}")
                
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
                
                st.markdown("**Saved Files:**")
                for file_info in saved_files:
                    st.markdown(f"- 📄 {file_info['name']} ({file_info['size']} bytes)")


def handle_execution(tasks_input):
    execution_col1, execution_col2, execution_col3 = st.columns([1, 2, 1])
    
    with execution_col2:
        if st.session_state.uploaded_files and tasks_input.strip():
            if not st.session_state.execution_in_progress:
                if st.button("🎯 LAUNCH AI AUDIT", type="primary", use_container_width=True):
                    tasks = [task.strip() for task in tasks_input.split('\n') if task.strip()]
                    
                    logger.info("🚀 User initiated audit execution")
                    logger.info(f"📝 Parsed {len(tasks)} tasks from input")
                    for i, task in enumerate(tasks, 1):
                        logger.info(f"   {i}. 🎯 {task}")
                    
                    if tasks:
                        st.session_state.execution_in_progress = True
                        logger.info("⚡ Execution started - setting progress flag")
                        
                        with st.spinner("🔄 Executing audit... This may take a few minutes"):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            progress_bar.progress(20)
                            status_text.text("🔍 Analyzing uploaded files...")
                            logger.info("🔍 Progress: 20% - Starting file analysis")
                            
                            start_time = time.time()
                            
                            data_path = f"data/{st.session_state.current_uuid}"
                            logger.info(f"📁 Execution data path: {data_path}")
                            
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


def main():
    configure_page()
    initialize_session_state()
    log_app_startup()
    
    setup_data_directory()
    
    render_header()
    render_reset_button()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_files = render_file_upload()
        handle_file_upload(uploaded_files)
    
    with col2:
        tasks_input = render_tasks_input()
    
    render_execution_section()
    handle_execution(tasks_input)
    
    if st.session_state.execution_results:
        logger.info("📊 Displaying audit results to user")
        results = st.session_state.execution_results
        logger.info(f"📋 Results summary: Success={results.get('success', False)}, "
                   f"Tasks={results.get('tasks_count', 0)}, "
                   f"Docs={results.get('documents_processed', 0)}")
        
        render_execution_results(results)


if __name__ == "__main__":
    logger.info("🎬 Starting Streamlit app main function")
    main()
    logger.info("🏁 Streamlit app main function completed") 