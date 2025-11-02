"""
URL Prioritizer Agent
Selects the most valuable pages from vendor and prospect websites for intelligence gathering.
Uses OpenAI GPT-4o-mini for fast URL filtering (40-60% faster than gpt-4o).
"""

from agno.agent import Agent
from pydantic import BaseModel, Field
from typing import List
import config


class PrioritizedURL(BaseModel):
    """Single prioritized URL with metadata"""
    url: str
    page_type: str = Field(description="e.g., 'about', 'case_study', 'pricing', 'blog'")
    priority: int = Field(description="1 (highest) to 10 (lowest)")
    reasoning: str


class URLPrioritizationResult(BaseModel):
    """Result containing prioritized URLs for both vendor and prospect"""
    vendor_selected_urls: List[PrioritizedURL]
    prospect_selected_urls: List[PrioritizedURL]


url_prioritizer = Agent(
    name="Strategic URL Selector",
    model=config.FAST_MODEL,  # gpt-4o-mini: 40-60% faster!
    instructions="""
    You are a content strategist selecting the most valuable pages for B2B sales intelligence.

    Given lists of URLs from vendor and prospect websites, select the TOP 10-15 MOST VALUABLE pages for each.

    PRIORITIZE:
    - /about, /about-us, /company, /team, /leadership
    - /products, /solutions, /platform, /features
    - /customers, /case-studies, /success-stories, /testimonials
    - /pricing, /plans
    - /blog (recent posts with dates in URL)
    - /industries, /use-cases, /resources

    AVOID:
    - Legal pages (/privacy, /terms, /legal, /cookies)
    - Career pages (/careers, /jobs, /join-us)
    - Support docs (/help, /docs, /support, /faq)
    - Login/signup pages (/login, /signup, /register)
    - Media/press pages (unless highly relevant)

    For each selected URL, provide:
    - page_type: Category of the page
    - priority: 1 (must have) to 10 (nice to have)
    - reasoning: Why this page is valuable for sales intelligence

    Return top 10-15 URLs per company, prioritized.
    """,
    output_schema=URLPrioritizationResult
)
