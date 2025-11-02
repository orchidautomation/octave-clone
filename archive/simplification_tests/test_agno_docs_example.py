"""
Test example directly from Agno docs to verify parallel block behavior
"""

from dotenv import load_dotenv
load_dotenv()

from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput

# Create agents
hn_agent = Agent(
    name="HN Researcher",
    tools=[HackerNewsTools()],
    instructions="Research tech news from Hacker News"
)

web_agent = Agent(
    name="Web Researcher",
    tools=[DuckDuckGoTools()],
    instructions="Research from web sources"
)

# Custom function to access parallel results
def combine_research(step_input: StepInput) -> StepOutput:
    print("\n" + "="*80)
    print("INSPECTING PARALLEL BLOCK ACCESS")
    print("="*80)

    # Get parallel step output by name
    parallel_output = step_input.get_step_content("parallel_research")

    print(f"\nparallel_output type: {type(parallel_output)}")
    print(f"parallel_output keys: {parallel_output.keys() if isinstance(parallel_output, dict) else 'N/A'}")

    # Access individual step content
    hn_content = parallel_output["research_hn"]
    web_content = parallel_output["research_web"]

    print(f"\nhn_content type: {type(hn_content)}")
    print(f"web_content type: {type(web_content)}")

    combined = f"HN: {hn_content}\n\nWeb: {web_content}"

    return StepOutput(content=combined, success=True)

# Create workflow
workflow = Workflow(
    name="Research Pipeline",
    steps=[
        Parallel(
            Step(name="research_hn", agent=hn_agent),
            Step(name="research_web", agent=web_agent),
            name="parallel_research"
        ),
        Step(name="combine", executor=combine_research)
    ]
)

print("Running Agno docs example workflow...")
workflow.print_response("AI developments", markdown=True)
