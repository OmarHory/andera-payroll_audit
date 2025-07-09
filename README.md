# 🧾 Junior Payroll Auditor - Usage Guide

## Quick Start

### 1. Run the Streamlit App
```bash
streamlit run streamlit_app.py
```

### 2. Using the Application

#### **📁 File Upload**
1. Click "Choose files to audit" in the File Upload Center
2. Select payroll documents (PDF, Excel, CSV, images, etc.)
3. Click "💾 Save Files" to create a UUID session and save files

#### **📝 Audit Tasks**
1. Choose from predefined templates:
   - **Standard Payroll Audit**: General payroll checks
   - **Compliance Check**: Labor law compliance
   - **Financial Analysis**: Cost and trend analysis
2. Or create custom tasks (one per line)

#### **⚡ Execution**
1. Once files are uploaded and tasks are defined, click "🚀 Execute Audit"
2. The system will process files using AI and generate a comprehensive report
3. Progress is tracked in real-time

#### **📊 Results**
- View execution metrics (time, files processed, etc.)
- Read the final AI-generated report
- Expand detailed task results
- Download results as JSON

## Architecture

### Core Components

#### **App Module** (`app/`)
- `graph.py`: Contains the main `invoke()` function and LangGraph implementation
- Processes files using multiple AI agents:
  - **Metadata Extractor**: Analyzes file content and purpose
  - **Task Parser**: Structures user tasks
  - **Document-to-Task Mapper**: Maps relevant documents to each task
  - **Execution Agent**: Performs the actual audit tasks
  - **Reporter**: Generates final comprehensive report

#### **Streamlit UI** (`streamlit_app.py`)
- Fancy hackathon-style interface with gradients and animations
- File upload with UUID-based session management
- Direct function calls (no API overhead)
- Real-time progress tracking
- Interactive results display

### Data Flow

1. **File Upload** → UUID folder creation in `data/` directory
2. **Task Definition** → User input or template selection
3. **Execution** → Direct call to `invoke(thread_id, data_path, tasks)`
4. **Processing** → AI agents analyze files and execute tasks
5. **Results** → Comprehensive report with detailed breakdowns

## Features

### 🎨 Hackathon-Ready UI
- Gradient backgrounds and modern styling
- Real-time progress indicators
- Interactive expandable sections
- Downloadable results

### 🔧 Technical Features
- **UUID Sessions**: Each upload session gets a unique identifier
- **Direct Integration**: No API overhead, direct function calls
- **Long-Running Support**: Progress tracking for lengthy processes
- **Redis Checkpointing**: Optional persistence (falls back gracefully)
- **Multi-Format Support**: PDF, Excel, CSV, images, text files

### 📊 AI-Powered Analysis
- Automatic document categorization
- Intelligent task-to-document mapping
- Comprehensive audit execution
- Structured reporting with pass/fail status

## Example Usage

### Standard Payroll Audit
```python
# This is what happens behind the scenes when you click Execute
result = invoke(
    thread_id="550e8400-e29b-41d4-a716-446655440000",
    data_path="data/550e8400-e29b-41d4-a716-446655440000",
    tasks=[
        "Check for payroll discrepancies and irregularities",
        "Verify employee overtime calculations",
        "Audit tax withholdings and deductions"
    ]
)
```

### Result Structure
```json
{
    "success": true,
    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
    "data_path": "data/550e8400-e29b-41d4-a716-446655440000",
    "tasks_count": 3,
    "documents_processed": 5,
    "report": "Comprehensive AI-generated audit report...",
    "execution_details": [
        {
            "task": "Check for payroll discrepancies",
            "output": "Analysis results...",
            "status": "PASS"
        }
    ]
}
```

## Requirements

- Python 3.12+
- OpenAI API key (set in `.env` file)
- Optional: Redis server for checkpointing
- All dependencies managed via `uv sync`

## Environment Setup

```bash
# Install dependencies
uv sync

# Set up environment variables
echo "OPENAI_API_KEY=your_key_here" > .env

# Optional: Start Redis for checkpointing
redis-server

# Run the application
streamlit run streamlit_app.py
```

---

**🚀 Ready for your hackathon demo!** The interface is designed to impress with its modern styling and smooth user experience. 