import time
from typing import List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.redis import RedisSaver
from states import State
from service.logger import logger
from service.nodes import (
    metadata_extractor, 
    tasks_parser, 
    document_to_task_mapper, 
    execution_agent, 
    reflector, 
    reporter, 
    should_continue
)
import os


def build_graph():
    logger.info("🏗️ Building LangGraph architecture...")
    
    try:
        builder = StateGraph(State)
        
        builder.add_node("metadata_extractor", metadata_extractor)
        builder.add_node("tasks_parser", tasks_parser)
        builder.add_node("document_to_task_mapper", document_to_task_mapper)
        builder.add_node("execution_agent", execution_agent)
        # builder.add_node("reflector", reflector)
        builder.add_node("reporter", reporter)

        builder.add_edge(START, "metadata_extractor")
        builder.add_edge("metadata_extractor", "tasks_parser")
        builder.add_edge("tasks_parser", "document_to_task_mapper")
        builder.add_edge("document_to_task_mapper", "execution_agent")
        builder.add_edge("execution_agent", "reporter")
        builder.add_edge("reporter", END)

        logger.info("🔗 Graph edges configured successfully")

        
        
        try:
            checkpointer = RedisSaver.from_conn_string(os.getenv("REDIS_URI"))
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

def compile_graph():
    graph = build_graph()
    return graph

def invoke(thread_id: str, data_path: str, tasks: List[str]) -> dict:
    logger.info(f"🎬 Starting audit execution for thread: {thread_id}")
    logger.info(f"📁 Data path: {data_path}")
    logger.info(f"📝 Tasks count: {len(tasks)}")
    
    try:
        
        tasks_string = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
        logger.info(f"📋 Formatted tasks:\n{tasks_string}")
        
        initial_state = State(
            data_path=data_path,
            tasks_raw=tasks_string
        )
        
        logger.info("🚀 Invoking graph execution...")
        start_time = time.time()

        graph = compile_graph()
        
        result = graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}}
        )
        
        execution_time = time.time() - start_time
        logger.info(f"⏱️ Graph execution completed in {execution_time:.2f} seconds")
        
        success = bool(result["reporter"] and len(result["execution_task_output"]) > 0)
        logger.info(f"✅ Execution success: {success}")
        
        execution_details = []
        for task_output in result["execution_task_output"]:
            execution_details.append({
                "task": task_output.task,
                "output": task_output.output,
                "status": task_output.pass_or_fail
            })
        
        response = {
            "success": success,
            "report": result["reporter"],
            "execution_details": execution_details,
            "documents_processed": len(result["docs_content_with_metadata"]),
            "tasks_count": len(result["tasks_parsed"].tasks) if result["tasks_parsed"] else 0,
            "execution_time": execution_time
        }
        
        logger.info("🎉 Audit execution completed successfully!")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error during audit execution: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "execution_time": time.time() - start_time if 'start_time' in locals() else 0
        } 