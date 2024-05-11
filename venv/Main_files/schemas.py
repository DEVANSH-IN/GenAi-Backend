from pydantic import BaseModel 
from typing import List

class Component(BaseModel):
  type: str  # Type of component (LLM, Agent, Tool)
  configuration: dict  # Dictionary to store specific configurations

# You can add other data models for workflows or other entities here as needed
class Workflow(BaseModel):  # Example for a workflow model (optional for now)
  component_ids: List[int]
  execution_order: List[int]  # Indexes corresponding to component_ids list
