"""
Test Agno docs example with structured Pydantic inputs/outputs
"""

from dotenv import load_dotenv
load_dotenv()

from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.hackernews import HackerNewsTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput

# Define structured input
class ResearchRequest(BaseModel):
    topic: str
    focus_areas: List[str] = Field(description="Areas to focus on")
    sources_required: int = Field(default=5)

# Define structured outputs for each step
class HNResearch(BaseModel):
    insights: List[str]
    trending_topics: List[str]

class WebResearch(BaseModel):
    findings: List[str]
    sources: List[str]

# Create agents with structured outputs
hn_agent = Agent(
    name="HN Researcher",
    model=OpenAIChat(id="gpt-4"),
    tools=[HackerNewsTools()],
    output_schema=HNResearch,
    instructions="Research from Hacker News"
)

web_agent = Agent(
    name="Web Researcher",
    model=OpenAIChat(id="gpt-4"),
    tools=[DuckDuckGoTools()],
    output_schema=WebResearch,
    instructions="Research from web"
)

# Custom function to combine structured outputs
def combine_research(step_input: StepInput) -> StepOutput:
    print("\n" + "="*80)
    print("INSPECTING STRUCTURED PYDANTIC OUTPUTS")
    print("="*80)

    # Get parallel results by name
    parallel_output = step_input.get_step_content("parallel_research")

    print(f"\nparallel_output type: {type(parallel_output)}")
    print(f"parallel_output keys: {parallel_output.keys() if isinstance(parallel_output, dict) else 'N/A'}")

    # Access structured content from each step
    hn_data = parallel_output["research_hn"]
    web_data = parallel_output["research_web"]

    print(f"\nhn_data type: {type(hn_data)}")
    print(f"hn_data value: {hn_data}")
    print(f"Is HNResearch instance? {isinstance(hn_data, HNResearch)}")

    print(f"\nweb_data type: {type(web_data)}")
    print(f"web_data value: {web_data}")
    print(f"Is WebResearch instance? {isinstance(web_data, WebResearch)}")

    # Try to access as if they were Pydantic models
    try:
        print(f"\n🔍 Attempting to access hn_data.insights...")
        if isinstance(hn_data, str):
            print(f"❌ hn_data is a string, needs deserialization")
        else:
            insights = hn_data.insights
            print(f"✅ Successfully accessed insights: {insights}")
    except Exception as e:
        print(f"❌ Failed to access: {type(e).__name__}: {str(e)}")

    # Combine structured data
    combined = f"""
    HN Data Type: {type(hn_data)}
    Web Data Type: {type(web_data)}
    """

    return StepOutput(content=combined, success=True)

# Create workflow with input schema
workflow = Workflow(
    name="Structured Research Pipeline",
    input_schema=ResearchRequest,
    steps=[
        Parallel(
            Step(name="research_hn", agent=hn_agent),
            Step(name="research_web", agent=web_agent),
            name="parallel_research"
        ),
        Step(name="combine", executor=combine_research)
    ]
)

print("Running structured Pydantic workflow...")

# Run with structured input
workflow.print_response(
    input=ResearchRequest(
        topic="AI developments",
        focus_areas=["LLMs", "Agents"],
        sources_required=10
    ),
    markdown=True
)
