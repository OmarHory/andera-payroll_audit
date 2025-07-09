from pydantic import BaseModel
from typing import Dict, List


class DocMetadata(BaseModel):
    name: str
    purpose: str
    possible_use_cases: str

class DocSelector(BaseModel):
    doc_path: str
    task: str

class State(BaseModel):
    data_path: str
    doc_metadata: List[DocMetadata] = []
    tasks_raw: str = ""
    tasks_parsed: list[str] = []
    doc_selector: list[DocSelector] = []
    reflector: str = ""
    reporter: str = ""

