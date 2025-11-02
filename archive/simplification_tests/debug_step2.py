"""
Debug script to test step2 with debug logging
"""

from agno.workflow import Workflow, Step, Parallel
from steps.step1_domain_validation import validate_vendor_domain, validate_prospect_domain
from steps.step2_homepage_scraping import scrape_vendor_homepage, scrape_prospect_homepage

# Create minimal workflow: Step 1 + Step 2
debug_workflow = Workflow(
    name="Debug Step 2",
    steps=[
        Parallel(
            Step(name="validate_vendor", executor=validate_vendor_domain),
            Step(name="validate_prospect", executor=validate_prospect_domain),
            name="parallel_validation"
        ),
        Parallel(
            Step(name="scrape_vendor_home", executor=scrape_vendor_homepage),
            Step(name="scrape_prospect_home", executor=scrape_prospect_homepage),
            name="parallel_homepage_scraping"
        )
    ]
)

# Run with test input
workflow_input = {
    "vendor_domain": "https://octavehq.com",
    "prospect_domain": "https://sendoso.com"
}

print("Running Step 1 + Step 2 with debug logging...")
result = debug_workflow.run(input=workflow_input)

print("\n" + "="*80)
print("WORKFLOW COMPLETE")
print("="*80)
print(f"Result type: {type(result)}")
print(f"Result.content type: {type(result.content)}")
