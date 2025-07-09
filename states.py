from pydantic import BaseModel, Field
from typing import Dict, List, TypedDict



class DocMetadata(BaseModel):
    name: str = Field(description="The name of the document", default="")
    purpose: str = Field(description="The purpose of the document", default="")
    possible_use_cases: str = Field(description="The possible use cases of the document", default="")

class DocumentWithMetadata(BaseModel):
    name: str = Field(description="The name of the document", default="")
    purpose: str = Field(description="The purpose of the document", default="")
    possible_use_cases: str = Field(description="The possible use cases of the document", default="")
    content: str = Field(description="The content of the document", default="")

class Task(BaseModel):
    task_id: str = Field(description="The id of the task", default="")
    task: str = Field(description="The task to be executed", default="")
class Tasks(BaseModel):
    tasks: List[Task] = Field(description="The tasks to be executed", default=[])

class DocumentToTaskMapper(BaseModel):
    docs: List[str] = Field(description="The documents that are most relevant to the task", default=[])
    task: str = Field(description="The task", default="")

class ExecutionAgent(BaseModel):
    task_id: str = Field(description="The id of the task", default="")
    output: str = Field(description="The output of the task", default="")

class State(BaseModel):
    data_path: str = Field(description="The path to the data", default="") #input
    tasks_raw: str = Field(description="The raw tasks", default="") #input


    docs_content_with_metadata: List[DocumentWithMetadata] = Field(description="The content of the documents with metadata", default=[])
    tasks_parsed: Tasks = Field(description="The parsed tasks", default=Tasks(tasks=[]))
    document_to_task_mapper: List[DocumentToTaskMapper] = Field(description="The documents selected for the tasks", default=[])
    execution_task_output: List[ExecutionAgent] = Field(description="The execution agent", default=[])

    reflector: str = Field(description="The reflector", default="")
    reporter: str = Field(description="The reporter", default="")

    task_max_iterations: int = Field(description="The maximum number of iterations for the task", default=1)
