from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel 
from schemas import Component, Workflow


from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from openagi.agent import Agent 
from openagi.tools.integrations.duckducksearch import DuckDuckGoSearchTool 
from openagi.llms.azure import AzureChatOpenAIModel 
from openagi.init_agent import kickOffAgents 

app = FastAPI()

class Component(BaseModel):
  type: str  # Type of component (LLM, Agent, Tool)
  configuration: dict  # Dictionary to store specific configurations

# In-memory storage (replace with database for persistence)
components = []

# Define SQLAlchemy base
Base = declarative_base()

# Define SQLAlchemy models
class ComponentDB(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    configuration = Column(String)

class WorkflowDB(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    component_ids = Column(String)
    execution_order = Column(String)

# Database URL (replace with PostgreSQL connection string)
DATABASE_URL = "postgresql://username:password@localhost/db_name"

# Create engine and metadata
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Bind the engine to the Base metadata
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Route handlers
@app.post("/components")
async def add_component(component: Component):
    db_component = ComponentDB(**component.dict())
    db = SessionLocal()
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    db.close()
    return {"message": "Component added successfully"}




@app.post("/components")
async def add_component(component: Component = Body(...)):
  components.append(component)
  return {"message": "Component added successfully"}

@app.get("/components")
async def get_components():
  return components

@app.put("/components/{component_id}")
async def configure_component(component_id: int, updated_config: Component = Body(...)):
  if component_id >= len(components):
    return {"error": "Component not found"}
  components[component_id].configuration.update(updated_config.configuration)
  return {"message": "Component configuration updated"}



# Route to delete a specific component by its index
@app.delete("/components/{component_id}")
async def delete_component(component_id: int):
    if component_id < 0 or component_id >= len(components):
        raise HTTPException(status_code=404, detail="Component not found")
    del components[component_id]
    return {"message": "Component deleted successfully"}



@app.post("/workflows")
async def add_workflow(workflow: Workflow = Body(...)):
  # Implement logic to store the workflow (replace with database later)
  workflow.append(workflow)  # Assuming workflows is a list to store workflows
  return {"message": "Workflow added successfully"}


@app.get("/workflows")
async def get_workflows():
  return Workflow  # Assuming workflows is a list containing stored workflows







#this is agent call for main 
if __name__ == "__main__":
    agent_list = [
        Agent(
            agentName="RESEARCHER",  # name
            role="RESEARCH EXPERT",  # role
            goal="search for latest trends in COVID-19 and Cancer treatment that includes medicines, physical exercises, overall management and prevention aspects",
            backstory="Has the capability to execute internet search tool",
            capability="search_executor",
            task="search internet for the goal for the trends after first half of 2023",
            output_consumer_agent="WRITER",  # the consumer agent after executing task
            tools_list=[DuckDuckGoSearchTool],
        ),
        Agent(
            agentName="WRITER",
            role="SUMMARISING EXPERT",
            goal="summarize input into presentable points",
            backstory="Expert in summarising the given text",
            capability="llm_task_executor",
            task="summarize points to present to health care professionals and general public separately",
            output_consumer_agent="EMAILER",
        ),
        Agent(
            agentName="EMAILER",
            role="EMAIL CREATOR",
            goal="composes the email based on the content",
            backstory="Good in composing precise emails",
            capability="llm_task_executor",
            task="composes email based on summary to doctors and general public separately into a file with subject-summary and details",
            output_consumer_agent="HGI",
        ),
    ]

    config = AzureChatOpenAIModel.load_from_yml_config()
    llm = AzureChatOpenAIModel(config=config)
    kickOffAgents(agent_list, [agent_list[0]], llm=llm)
