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
    # Get parallel step outputs as StepOutput objects
    parallel_output = step_input.get_step_output("parallel_research")

    # Access the StepOutput objects for each parallel step
    hn_step_output = parallel_output.get("research_hn")
    web_step_output = parallel_output.get("research_web")

    # Access the structured content from StepOutput.content
    hn_data: HNResearch = hn_step_output.content
    web_data: WebResearch = web_step_output.content

    # Combine structured data
    combined = f"""
    HN Insights: {', '.join(hn_data.insights)}
    HN Trending: {', '.join(hn_data.trending_topics)}

    Web Findings: {', '.join(web_data.findings)}
    Web Sources: {', '.join(web_data.sources)}
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

# Run with structured input
workflow.print_response(
    input=ResearchRequest(
        topic="AI developments",
        focus_areas=["LLMs", "Agents"],
        sources_required=10
    ),
    markdown=True
)