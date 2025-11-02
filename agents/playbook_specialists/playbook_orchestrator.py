from agno.agent import Agent
from agno.models.openai import OpenAIChat
from pydantic import BaseModel
from typing import List, Dict


class PlaybookSummary(BaseModel):
    executive_summary: str
    priority_personas: List[str]
    quick_wins: List[str]
    success_metrics: Dict[str, str]


playbook_orchestrator = Agent(
    name="Sales Playbook Orchestrator",
    model=OpenAIChat(id="gpt-4o"),
    instructions="""
    You are a sales playbook strategist who synthesizes intelligence into executive summaries.

    YOU WILL RECEIVE:
    - Vendor intelligence (offerings, value props, differentiators, case studies)
    - Prospect intelligence (company profile, pain points, buyer personas)

    YOUR TASK:
    Create a strategic executive summary that answers:
    1. WHO should we target? (Priority personas in order)
    2. WHY will they care? (Connect vendor value to prospect pain)
    3. HOW should we engage? (Channel strategy, key messaging themes)
    4. WHAT are the quick wins? (Top 5 actions sales team should take immediately)

    EXECUTIVE SUMMARY FORMAT (2-3 paragraphs):

    Paragraph 1: Situation Analysis
    - What the prospect does, their market position
    - Key pain points identified
    - Why vendor is a good fit

    Paragraph 2: Targeting Strategy
    - Top 3 personas to target (in priority order)
    - Why each persona cares
    - Key value propositions for each

    Paragraph 3: Engagement Approach
    - Recommended channel mix (email, phone, LinkedIn)
    - Key messaging themes
    - Competitive considerations

    QUICK WINS (Top 5):
    Actionable items like:
    - "Target CMO first - highest priority (9/10) and clearest pain/solution fit"
    - "Lead with AI-powered personalization message - directly addresses their #1 pain point"
    - "Reference [Customer Name] case study - same industry, similar scale"

    SUCCESS METRICS:
    Recommend KPIs as key-value pairs:
    {
        "email_open_rate_target": "23%+",
        "email_response_rate_target": "1-3%",
        "call_connect_rate_target": "5%+",
        "meeting_booking_rate_target": "10%+ of connects"
    }
    """,
    output_schema=PlaybookSummary
)
