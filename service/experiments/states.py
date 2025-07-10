from pydantic import BaseModel, Field
from typing import List



class DocMetadata(BaseModel):
    name: str = Field(description="The name of the document", default="")
    purpose: str = Field(description="The purpose of the document", default="")
    possible_use_cases: str = Field(description="The possible use cases of the document", default="")

class DocumentWithMetadata(BaseModel):
    name: str = Field(description="The name of the document", default="")
    purpose: str = Field(description="The purpose of the document", default="")
    possible_use_cases: str = Field(description="The possible use cases of the document", default="")
    content: str = Field(description="The content of the document", default="")

class Tasks(BaseModel):
    tasks: List[str] = Field(description="The tasks to be executed", default=[])

class DocumentToTaskMapper(BaseModel):
    docs: List[DocumentWithMetadata] = Field(description="The documents that are most relevant to the task", default=[])
    task: str = Field(description="The description of the task", default="")

class ExecutionAgent(BaseModel):
    task: str = Field(description="The description of the task", default="")
    output: str = Field(description="The output of the task", default="")
    pass_or_fail: str = Field(description="PASS if the task is executed successfully, FAIL if the task is not executed successfully", default="")
    file_name: str = Field(description="The name of the file", default="")

class Reporter(BaseModel):
    output: str = Field(description="The output of the task", default="")

class RelevanceToSoxAndFinancialStandards(BaseModel):
    is_relevant: bool = Field(description="Whether the task is relevant to SOX and financial standards", default=False)
    reason: str = Field(description="The reason for the relevance", default="")

class State(BaseModel):
    data_path: str = Field(description="The path to the data", default="") #input
    tasks_raw: str = Field(description="The raw tasks", default="") #input


    docs_content_with_metadata: List[DocumentWithMetadata] = Field(description="The content of the documents with metadata", default=[])
    tasks_parsed: Tasks = Field(description="The parsed tasks", default=Tasks(tasks=[]))
    
    document_to_task_mapper: List[DocumentToTaskMapper] = Field(description="The documents selected for the tasks", default=[])
    execution_task_output: List[ExecutionAgent] = Field(description="The execution agent", default=[])

    reflector: str = Field(description="The reflector", default="")
    reporter: str = Field(description="The reporter", default="")
    
    task_max_iterations: int = Field(description="The maximum number of iterations for the task", default=5)
    task_current_iteration: int = Field(description="The current iteration of the task", default=0)

    is_in_reflection: bool = Field(description="Whether the agent is in reflection", default=False)
    relevance_to_sox_and_financial_standards: RelevanceToSoxAndFinancialStandards = Field(description="The relevance to SOX and financial standards", default=RelevanceToSoxAndFinancialStandards(is_relevant=True, reason=""))

