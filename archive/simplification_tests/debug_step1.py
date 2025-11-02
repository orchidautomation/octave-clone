"""
Debug script to see what Step 1 actually returns
"""

from agno.workflow import Workflow, Step, Parallel, StepInput, StepOutput
from steps.step1_domain_validation import validate_vendor_domain, validate_prospect_domain

# Create minimal workflow with just step 1
debug_workflow = Workflow(
    name="Debug Step 1",
    steps=[
        Parallel(
            Step(name="validate_vendor", executor=validate_vendor_domain),
            Step(name="validate_prospect", executor=validate_prospect_domain),
            name="parallel_validation"
        )
    ]
)

# Run with test input
workflow_input = {
    "vendor_domain": "https://octavehq.com",
    "prospect_domain": "https://sendoso.com"
}

print("Running Step 1 validation...")
result = debug_workflow.run(input=workflow_input)

print("\n" + "="*80)
print("RESULT INSPECTION")
print("="*80)
print(f"Result type: {type(result)}")
print(f"Result.content type: {type(result.content)}")
print(f"\nResult.content keys: {result.content.keys() if isinstance(result.content, dict) else 'N/A'}")

if isinstance(result.content, dict):
    for key, value in result.content.items():
        print(f"\n{key}:")
        print(f"  Type: {type(value)}")
        print(f"  Value: {value}")
