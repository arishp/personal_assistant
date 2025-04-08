# from IPython.display import Image, display
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from backend.graph import builder
from dotenv import load_dotenv
import uuid 
# from IPython.display import Markdown
import streamlit as st
import asyncio

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

st.title('My Deep Research')

topic = st.text_input("Enter your query")

if st.button('Deep Research'):

    async def first_response():
        async for event in graph.astream({"topic":topic,}, thread, stream_mode="updates"):
            if '__interrupt__' in event:
                interrupt_value = event['__interrupt__'][0].value
                print(interrupt_value)
    asyncio.run(first_response())

    async def second_response():
        async for event in graph.astream(Command(resume="Include individuals sections for each topic"), thread, stream_mode="updates"):
            if '__interrupt__' in event:
                interrupt_value = event['__interrupt__'][0].value
                print(interrupt_value)
    asyncio.run(second_response())

    async def third_response():
        async for event in graph.astream(Command(resume=True), thread, stream_mode="updates"):
            print(event)
            print("\n")
    asyncio.run(third_response())

    final_state = graph.get_state(thread)
    report = final_state.values.get('final_report')
    st.write(report)