import streamlit as st
import json
from ui.utils import format_execution_time
from ui.markdown_viewer import render_markdown, render_report_section


def render_header():
    st.markdown('''
    <div class="header-section floating">
        <h1 class="main-header">🧾 Junior Payroll Auditor</h1>
        <p class="subtitle">AI-Powered Payroll Analysis & Auditing System 🚀</p>
    </div>
    ''', unsafe_allow_html=True)


def render_reset_button():
    col_reset1, col_reset2, col_reset3 = st.columns([2, 1, 2])
    with col_reset2:
        if st.button("🔄 Reset Session", use_container_width=True):
            from ui.logger import logger
            logger.info("🔄 User requested session reset")
            if st.session_state.current_uuid:
                logger.info(f"🗑️ Clearing session: {st.session_state.current_uuid}")
            st.session_state.clear()
            logger.info("✅ Session reset completed")
            st.rerun()


def render_file_upload():
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
    
    return uploaded_files


def render_tasks_input():
    st.markdown("""
    <div class="task-section floating">
        <h3>✨ Custom Audit Tasks</h3>
    </div>
    """, unsafe_allow_html=True)
    
    tasks_input = st.text_area(
        "🎯 Define Your Audit Mission",
        value="",
        height=250,
        placeholder="🚀 Enter your audit tasks here (one per line):\n\n💡 Examples:\n• Check for payroll discrepancies and irregularities\n• Verify employee overtime calculations\n• Audit tax withholdings and deductions\n• Review salary and wage accuracy\n• Validate benefits calculations\n• Ensure labor law compliance\n• Analyze payroll cost trends",
        disabled=st.session_state.execution_in_progress,
        help="Each line will be treated as a separate audit task. Be specific for better results!"
    )
    
    return tasks_input


def render_execution_section():
    st.markdown("""
    <div class="execution-section floating">
        <h3>🚀 AI Execution Command Center</h3>
    </div>
    """, unsafe_allow_html=True)


def render_execution_results(results):
    st.markdown("""
    <div class="results-section floating">
        <h3>🎉 Audit Intelligence Report</h3>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.markdown("### 📋 Final Report")
        # Use our custom renderer for the report text
        report_text = results.get("report", "No report available")
        # This will handle special characters and proper spacing
        render_markdown(report_text)
        
        if results.get("execution_details"):
            st.markdown("### 🔍 Detailed Task Results")
            
            for i, detail in enumerate(results["execution_details"], 1):
                with st.expander(f"Task {i}: {detail['task']}", expanded=i==1):
                    status_color = "green" if detail['status'] == "PASS" else "red"
                    st.markdown(f"**Status:** :{status_color}[{detail['status']}]")
                    st.markdown(f"**Output:**")
                    # Use our custom markdown renderer for consistent formatting
                    render_markdown(detail['output'])
        
        with st.expander("🔧 Raw Results (Debug)", expanded=False):
            st.json(results)
    
    else:
        st.error(f"❌ Execution failed: {results.get('error', 'Unknown error')}")
    
    if st.button("📊 Export Intelligence Report"):
        from ui.logger import logger
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