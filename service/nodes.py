import os
from service.states import State, DocMetadata, Tasks, DocumentWithMetadata, DocumentToTaskMapper, ExecutionAgent, Reporter, RelevanceToSoxAndFinancialStandards
from service.prompts import (
    METADATA_EXTRACTOR_PROMPT, 
    TASK_PARSER_PROMPT, 
    DOCUMENT_TO_TASK_MAPPER_PROMPT,
    EXECUTION_AGENT_PROMPT,
    REPORTER_PROMPT,
    REFLECTOR_PROMPT,
    RELEVANCE_TO_SOX_AND_FINANCIAL_STANDARDS_PROMPT,
)
from service.parsers import parse_directory_files
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from service.logger import logger
import dotenv

dotenv.load_dotenv()

model = ChatOpenAI(model="o4-mini", reasoning_effort="high", api_key=os.getenv("OPENAI_API_KEY"))


def relevance_to_SOX_and_financial_standards(state: State):
    logger.info("🔍 Starting relevance to SOX and financial standards...")
    
    messages = [
        SystemMessage(content=RELEVANCE_TO_SOX_AND_FINANCIAL_STANDARDS_PROMPT),
        HumanMessage(content=str(state.tasks_raw))
    ]

    response = model.with_structured_output(RelevanceToSoxAndFinancialStandards).invoke(messages)
    state.relevance_to_sox_and_financial_standards = response
    return state

def metadata_extractor(state: State):
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
    logger.info("🔗 Starting document-to-task mapping...")
    
    try:
        total_tasks = len(state.tasks_parsed.tasks)
        logger.info(f"🗂️ Mapping {len(state.docs_content_with_metadata)} documents to {total_tasks} tasks")

        for i, task in enumerate(state.tasks_parsed.tasks, 1):
            logger.info(f"🔄 Mapping task {i}/{total_tasks}: {task}")
            
            organized_docs = ""
            for doc in state.docs_content_with_metadata: 
                organized_docs += f"\n\nFile Name: {doc.name}\nFile Purpose: {doc.purpose}\nFile Possible Use Cases: {doc.possible_use_cases}\nFile Content: \n<document_content {doc.name}>\n{doc.content}\n</document_content {doc.name}>\n\n"
            
            messages = [
                SystemMessage(content=DOCUMENT_TO_TASK_MAPPER_PROMPT),
                HumanMessage(content=f"Task: {task}\nDocuments: {organized_docs}")
            ]

            response = model.with_structured_output(DocumentToTaskMapper).invoke(messages)
            state.document_to_task_mapper.append(response)
            
            logger.info(f"✅ Mapped {len(response.docs)} documents to task: {task}")
            logger.info(f"   📋 Relevant documents: {', '.join([doc.name for doc in response.docs]) if response.docs else 'None'}")

        logger.info(f"🎉 Document-to-task mapping completed! {total_tasks} tasks mapped successfully")
        return state
        
    except Exception as e:
        logger.error(f"❌ Error in document-to-task mapping: {str(e)}")
        raise


def execution_agent(state: State):
    logger.info("⚡ Starting task execution...")
    
    try:
        total_items = len(state.document_to_task_mapper)
        logger.info(f"🚀 Executing {total_items} audit tasks")
        
        for i, item in enumerate(state.document_to_task_mapper, 1):
            logger.info(f"🎯 Executing task {i}/{total_items}: {item.task}")
            
            docs_content = ""
            for doc in item.docs:
                docs_content += f"\n\nFile Name: {doc.name}\nFile Content: \n<document_content {doc.name}>\n{doc.content}\n</document_content {doc.name}>\n\n"
            
            messages = [
                SystemMessage(content=EXECUTION_AGENT_PROMPT),
                HumanMessage(content=f"Task: {str(item.task)}\nDocuments: \n{docs_content}")
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


def reflector(state: State):
    logger.info("🔍 Starting reflection on task execution...")
    
    try:
        logger.info("🧠 Reflecting on task execution results...")
        state.is_in_reflection = True

        messages = [
            SystemMessage(content=REFLECTOR_PROMPT),
            HumanMessage(content=str(state.execution_task_output))
        ]

        response = model.invoke(messages)
        state.reflector = response.content
        
        logger.info("✅ Reflection completed successfully!")
        logger.info(f"🔍 Reflection preview: {state.reflector[:200]}..." if len(state.reflector) > 200 else f"🔍 Reflection: {state.reflector}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error in reflection: {str(e)}")
        raise


def reporter(state: State):
    logger.info("📊 Starting final report generation...")
    
    try:
        total_outputs = len(state.execution_task_output)
        logger.info(f"📋 Generating report from {total_outputs} task executions")

        if not state.relevance_to_sox_and_financial_standards.is_relevant:
            state.reporter = "The given tasks are not relevant to SOX and financial standards, because of " + state.relevance_to_sox_and_financial_standards.reason
            logger.info("✅ Final report generated successfully!")
            logger.info(f"📄 Report length: {len(state.reporter)} characters")
            logger.info(f"📊 Report preview: {state.reporter[:200]}..." if len(state.reporter) > 200 else f"📊 Report: {state.reporter}")
            return state

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


def should_continue(state: State):
    logger.info("🔄 Evaluating whether to continue with reflection...")
    
    state.is_in_reflection = True
    state.task_current_iteration += 1
    
    logger.info(f"🔢 Current iteration: {state.task_current_iteration}/{state.task_max_iterations}")
    
    if state.task_current_iteration < state.task_max_iterations:
        logger.info("🔄 Continuing with reflection cycle...")
        return 'continue'
    else:
        logger.info("🏁 Maximum iterations reached, stopping reflection...")
        return 'stop' 


def is_relevant(state: State):
    logger.info("🔍 Evaluating relevance to SOX and financial standards...")
    
    if state.relevance_to_sox_and_financial_standards.is_relevant:
        logger.info("✅ Task is relevant to SOX and financial standards")
        return "continue"
    else:
        logger.info("❌ Task is not relevant to SOX and financial standards")
        return "stop"