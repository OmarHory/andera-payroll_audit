import os
import uuid
import logging
from typing import List
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.redis import RedisSaver

from states import State, DocMetadata, Tasks, DocumentWithMetadata, DocumentToTaskMapper, ExecutionAgent, Reporter
from prompts import (
    METADATA_EXTRACTOR_PROMPT, 
    TASK_PARSER_PROMPT, 
    DOCUMENT_TO_TASK_MAPPER_PROMPT, 
    EXECUTION_AGENT_PROMPT,
    REPORTER_PROMPT
)
from parsers import parse_directory_files
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

import dotenv
dotenv.load_dotenv()

# Configure logging with emojis and file output
def setup_logger():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("payroll_auditor")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(f"logs/payroll_auditor_{timestamp}.log", encoding='utf-8')
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
logger = setup_logger()

# Initialize the model
model = ChatOpenAI(model="o4-mini", reasoning_effort="high", api_key=os.getenv("OPENAI_API_KEY"))


def metadata_extractor(state: State):
    """Extract metadata from all files in the data path"""
    logger.info("🔍 Starting metadata extraction from files...")
    
    try:
        files = parse_directory_files(state.data_path)
        logger.info(f"📁 Found {len(files)} files to process in {state.data_path}")
        
        for i, file in enumerate(files, 1):
            logger.info(f"🔎 Processing file {i}/{len(files)}: {file['file_name']}")
            
            messages = [
                SystemMessage(content=METADATA_EXTRACTOR_PROMPT),
                HumanMessage(content=f"File Name: {file['file_name']}\nFile Content: \n{file['content']}")
            ]
            
            response = model.with_structured_output(DocMetadata).invoke(messages)
            
            # Convert any dict responses to strings to avoid Pydantic warnings
            def safe_str(value):
                if isinstance(value, dict):
                    return str(value.get('name', value.get('text', str(value))))
                return str(value) if value else ""
            
            state.docs_content_with_metadata.append(
                DocumentWithMetadata(
                    name=safe_str(response.name), 
                    purpose=safe_str(response.purpose), 
                    possible_use_cases=safe_str(response.possible_use_cases), 
                    content=file['content']
                )
            )
            logger.info(f"✅ Successfully processed: {file['file_name']} | Purpose: {response.purpose}")
        
        logger.info(f"🎉 Metadata extraction completed! Processed {len(files)} files successfully")
        return state
        
    except Exception as e:
        logger.error(f"❌ Error in metadata extraction: {str(e)}")
        raise


def tasks_parser(state: State):
    """Parse the raw tasks string into structured tasks"""
    logger.info("📋 Starting task parsing...")
    
    try:
        tasks = state.tasks_raw
        logger.info(f"📝 Raw tasks input: {tasks[:100]}..." if len(tasks) > 100 else f"📝 Raw tasks input: {tasks}")

        messages = [
            SystemMessage(content=TASK_PARSER_PROMPT),
            HumanMessage(content=tasks)
        ]

        response = model.with_structured_output(Tasks).invoke(messages)
        state.tasks_parsed = response
        
        logger.info(f"✅ Successfully parsed {len(response.tasks)} tasks:")
        for i, task in enumerate(response.tasks, 1):
            logger.info(f"   {i}. 🎯 {task}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error in task parsing: {str(e)}")
        raise


def document_to_task_mapper(state: State):
    """Map documents to specific tasks"""
    logger.info("🔗 Starting document-to-task mapping...")
    
    try:
        total_tasks = len(state.tasks_parsed.tasks)
        logger.info(f"🗂️ Mapping {len(state.docs_content_with_metadata)} documents to {total_tasks} tasks")

        for i, task in enumerate(state.tasks_parsed.tasks, 1):
            logger.info(f"🔄 Mapping task {i}/{total_tasks}: {task}")
            
            messages = [
                SystemMessage(content=DOCUMENT_TO_TASK_MAPPER_PROMPT),
                HumanMessage(content=f"Task: {task}\nDocuments: {str(state.docs_content_with_metadata)}")
            ]

            response = model.with_structured_output(DocumentToTaskMapper).invoke(messages)
            state.document_to_task_mapper.append(response)
            
            logger.info(f"✅ Mapped {len(response.docs)} documents to task: {task}")
            logger.info(f"   📋 Relevant documents: {', '.join(response.docs) if response.docs else 'None'}")

        logger.info(f"🎉 Document-to-task mapping completed! {total_tasks} tasks mapped successfully")
        return state
        
    except Exception as e:
        logger.error(f"❌ Error in document-to-task mapping: {str(e)}")
        raise


def execution_agent(state: State):
    """Execute the mapped tasks"""
    logger.info("⚡ Starting task execution...")
    
    try:
        total_items = len(state.document_to_task_mapper)
        logger.info(f"🚀 Executing {total_items} audit tasks")
        
        for i, item in enumerate(state.document_to_task_mapper, 1):
            logger.info(f"🎯 Executing task {i}/{total_items}: {item.task}")
            
            messages = [
                SystemMessage(content=EXECUTION_AGENT_PROMPT),
                HumanMessage(content=f"Task: {str(item.task)}\nDocuments: \n{str(item.docs)}")
            ]

            response = model.with_structured_output(ExecutionAgent).invoke(messages)
            state.execution_task_output.append(response)
            
            status_emoji = "✅" if response.pass_or_fail == "PASS" else "❌"
            logger.info(f"{status_emoji} Task {i} completed with status: {response.pass_or_fail}")
            logger.info(f"   📊 Output preview: {response.output[:150]}..." if len(response.output) > 150 else f"   📊 Output: {response.output}")
        
        passed_tasks = sum(1 for item in state.execution_task_output if item.pass_or_fail == "PASS")
        failed_tasks = total_items - passed_tasks
        
        logger.info(f"🎉 Task execution completed!")
        logger.info(f"   ✅ Passed: {passed_tasks} tasks")
        logger.info(f"   ❌ Failed: {failed_tasks} tasks")
        logger.info(f"   📊 Success rate: {(passed_tasks/total_items)*100:.1f}%")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error in task execution: {str(e)}")
        raise


def reporter(state: State):
    """Generate final report from all task executions"""
    logger.info("📊 Starting final report generation...")
    
    try:
        total_outputs = len(state.execution_task_output)
        logger.info(f"📋 Generating report from {total_outputs} task executions")

        messages = [
            SystemMessage(content=REPORTER_PROMPT),
            HumanMessage(content=str(state.execution_task_output))
        ]

        response = model.with_structured_output(Reporter).invoke(messages)
        state.reporter = response.output
        
        logger.info("✅ Final report generated successfully!")
        logger.info(f"📄 Report length: {len(state.reporter)} characters")
        logger.info(f"📊 Report preview: {state.reporter[:200]}..." if len(state.reporter) > 200 else f"📊 Report: {state.reporter}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error in report generation: {str(e)}")
        raise


def build_graph():
    """Build and return the configured LangGraph"""
    logger.info("🏗️ Building LangGraph architecture...")
    
    try:
        builder = StateGraph(State)
        
        # Add nodes
        builder.add_node("metadata_extractor", metadata_extractor)
        builder.add_node("tasks_parser", tasks_parser)
        builder.add_node("document_to_task_mapper", document_to_task_mapper)
        builder.add_node("execution_agent", execution_agent)
        builder.add_node("reporter", reporter)

        # Add edges
        builder.add_edge(START, "metadata_extractor")
        builder.add_edge("metadata_extractor", "tasks_parser")
        builder.add_edge("tasks_parser", "document_to_task_mapper")
        builder.add_edge("document_to_task_mapper", "execution_agent")
        builder.add_edge("execution_agent", "reporter")
        builder.add_edge("reporter", END)

        logger.info("🔗 Graph edges configured successfully")

        # Configure Redis checkpointer
        REDIS_URI = "redis://localhost:6379/0"
        
        try:
            checkpointer = RedisSaver.from_conn_string(REDIS_URI)
            checkpointer.setup()
            graph = builder.compile(checkpointer=checkpointer)
            logger.info("✅ Graph compiled with Redis checkpointing enabled")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, running without checkpointing: {e}")
            graph = builder.compile()
            logger.info("✅ Graph compiled without checkpointing")
        
        logger.info("🎉 LangGraph build completed successfully!")
        return graph
        
    except Exception as e:
        logger.error(f"❌ Error building graph: {str(e)}")
        raise


def invoke(thread_id: str, data_path: str, tasks: List[str]) -> dict:
    """
    Main invoke function that runs the payroll audit graph
    
    Args:
        thread_id: UUID string to be used as the thread_id for checkpointing
        data_path: Path to the directory containing files to analyze
        tasks: List of tasks to execute on the data
    
    Returns:
        Dictionary containing the final report and execution details
    """
    start_time = datetime.now()
    logger.info("🚀 Starting Junior Payroll Auditor execution")
    logger.info(f"🆔 Thread ID: {thread_id}")
    logger.info(f"📁 Data path: {data_path}")
    logger.info(f"📝 Number of tasks: {len(tasks)}")
    logger.info(f"⏰ Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Log all tasks
    logger.info("📋 Task list:")
    for i, task in enumerate(tasks, 1):
        logger.info(f"   {i}. 🎯 {task}")
    
    try:
        # Validate inputs
        if not os.path.exists(data_path):
            error_msg = f"Data path does not exist: {data_path}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        if not tasks:
            error_msg = "At least one task must be provided"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        logger.info("✅ Input validation passed")
        
        # Convert tasks list to string
        tasks_raw = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
        logger.info(f"📝 Tasks formatted for processing")
        
        # Initialize state
        initial_state = State(
            data_path=data_path,
            tasks_raw=tasks_raw
        )
        logger.info("🔧 Initial state created")
        
        # Build and run the graph
        graph = build_graph()
        
        # Run with checkpointing if available
        config = {"configurable": {"thread_id": thread_id}}
        logger.info("🎬 Starting graph execution...")
        
        final_state = None
        step_count = 0
        for state in graph.stream(initial_state, config):
            step_count += 1
            node_name = list(state.keys())[-1] if state else "unknown"
            logger.info(f"🔄 Completed step {step_count}: {node_name}")
            final_state = state
        
        # Extract the final state from the last node
        if final_state:
            # Get the state from the last executed node
            last_node_name = list(final_state.keys())[-1]
            final_state_obj = final_state[last_node_name]
            logger.info(f"✅ Graph execution completed successfully after {step_count} steps")
        else:
            error_msg = "Graph execution failed - no final state"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Create result
        result = {
            "success": True,
            "thread_id": thread_id,
            "data_path": data_path,
            "tasks_count": len(tasks),
            "documents_processed": len(final_state_obj.docs_content_with_metadata),
            "report": final_state_obj.reporter,
            "execution_details": [
                {
                    "task": item.task,
                    "output": item.output,
                    "status": item.pass_or_fail
                } for item in final_state_obj.execution_task_output
            ]
        }
        
        # Log final statistics
        logger.info("🎉 EXECUTION COMPLETED SUCCESSFULLY!")
        logger.info(f"⏱️ Total execution time: {execution_time:.2f} seconds")
        logger.info(f"📄 Documents processed: {result['documents_processed']}")
        logger.info(f"🎯 Tasks completed: {result['tasks_count']}")
        
        passed_tasks = sum(1 for detail in result['execution_details'] if detail['status'] == 'PASS')
        logger.info(f"✅ Successful tasks: {passed_tasks}/{result['tasks_count']}")
        logger.info(f"📊 Success rate: {(passed_tasks/result['tasks_count'])*100:.1f}%")
        logger.info(f"📋 Final report length: {len(result['report'])} characters")
        
        return result
        
    except Exception as e:
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        error_result = {
            "success": False,
            "error": str(e),
            "thread_id": thread_id,
            "data_path": data_path,
            "execution_time": execution_time
        }
        
        logger.error(f"💥 EXECUTION FAILED after {execution_time:.2f} seconds")
        logger.error(f"❌ Error: {str(e)}")
        logger.error(f"🆔 Thread ID: {thread_id}")
        logger.error(f"📁 Data path: {data_path}")
        
        return error_result


if __name__ == "__main__":
    # Example usage
    logger.info("🧪 Running test execution...")
    
    test_thread_id = str(uuid.uuid4())
    test_data_path = "./data"
    test_tasks = [
        "Check for payroll discrepancies",
        "Verify employee overtime calculations",
        "Audit tax withholdings"
    ]
    
    result = invoke(test_thread_id, test_data_path, test_tasks)
    
    logger.info("="*80)
    logger.info("🏁 FINAL RESULT:")
    logger.info("="*80)
    logger.info(f"�� Result: {result}") 