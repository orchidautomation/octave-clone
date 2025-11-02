from agno.agent import Agent
import config
from models.vendor_elements import TargetPersona
from typing import List
from pydantic import BaseModel


class TargetPersonasExtractionResult(BaseModel):
    target_personas: List[TargetPersona]


persona_extractor = Agent(
    name="Vendor ICP Persona Extractor",
    model=config.EXTRACTION_MODEL,  # gpt-4o-mini for fast extraction
    instructions="""
    You are an expert at identifying a vendor's ICP (Ideal Customer Profile) personas.

    IMPORTANT: You are extracting the types of buyers the VENDOR typically sells to.
    This is their target market profile, NOT specific personas at a particular prospect company.

    YOUR TASK:
    Extract ALL personas the vendor targets - who they typically sell to.

    For each persona:
    - Title: Job title (e.g., "CMO", "VP Sales", "Product Manager")
    - Department: Department or function
    - Responsibilities: Key responsibilities mentioned
    - Pain points: Problems this persona faces (mentioned or implied)
    - Sources: URLs where found (include page_type)

    Look for:
    - Persona-specific landing pages
    - "For [Role]" sections
    - Testimonials with titles (roles of their customers)
    - Use cases by role
    - Product messaging by audience
    - CTA language ("For marketing teams", etc.)

    Infer personas from:
    - Who testimonials are from (their customers' roles)
    - Who use cases target
    - Job titles in case studies
    - Role-based messaging
    - Department-specific solutions

    Examples of personas:
    - Chief Marketing Officer (CMO)
    - VP of Sales
    - Revenue Operations Manager
    - Product Manager
    - Customer Success Director

    Extract both explicit personas (directly mentioned) and implicit personas (inferred from content).

    Remember: These are the vendor's TYPICAL buyer personas (their ICP), not specific people at a prospect company.
    """,
    output_schema=TargetPersonasExtractionResult
)
