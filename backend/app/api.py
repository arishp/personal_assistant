from fastapi import APIRouter
from pydantic import BaseModel
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from app.graph import builder
from dotenv import load_dotenv
import uuid 

router = APIRouter()

class QueryRequest(BaseModel):
    input_text: str

class QueryResponse(BaseModel):
    response: str

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    load_dotenv()
    REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:

    1. Introduction (no research needed)
    - Brief overview of the topic area

    2. Main Body Sections:
    - Each section should focus on a sub-topic of the user-provided topic
    
    3. Conclusion
    - Aim for 1 structural element (either a list of table) that distills the main body sections 
    - Provide a concise summary of the report"""
    thread = {"configurable": {"thread_id": str(uuid.uuid4()),
                            "search_api": "tavily",
                            "planner_provider": "google-genai",
                            "planner_model": "gemini-2.0-flash-lite",
                            "writer_provider": "google-genai",
                            "writer_model": "gemini-2.0-flash-lite",
                            "max_search_depth": 1,
                            "report_structure": REPORT_STRUCTURE,
                            }}
    async for event in graph.astream({"topic":request,}, thread, stream_mode="updates"):
        pass
    async for event in graph.astream(Command(resume="Include individuals sections for each topic"), thread, stream_mode="updates"):
        pass
    async for event in graph.astream(Command(resume=True), thread, stream_mode="updates"):
        pass
    final_state = graph.get_state(thread)
    report = final_state.values.get('final_report')
    return QueryResponse(response=report)
