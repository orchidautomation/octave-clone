"""
Mock test to show how Pydantic models get serialized in parallel blocks
"""

from typing import List
from pydantic import BaseModel
from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput

# Define Pydantic models matching the Agno docs example
class VendorData(BaseModel):
    domain: str
    offerings: List[str]
    metrics: dict

class ProspectData(BaseModel):
    domain: str
    pain_points: List[str]
    company_size: str

# Mock executors that return Pydantic models in StepOutput
def mock_vendor_step(step_input: StepInput) -> StepOutput:
    """Returns Pydantic model in structured output"""
    vendor_model = VendorData(
        domain="https://vendor.com",
        offerings=["Product A", "Product B", "Service C"],
        metrics={"revenue": "10M", "employees": 50}
    )

    # Return the Pydantic model as content
    return StepOutput(
        content=vendor_model.model_dump(),  # Convert to dict
        success=True
    )

def mock_prospect_step(step_input: StepInput) -> StepOutput:
    """Returns Pydantic model in structured output"""
    prospect_model = ProspectData(
        domain="https://prospect.com",
        pain_points=["Issue 1", "Issue 2", "Challenge 3"],
        company_size="Enterprise"
    )

    return StepOutput(
        content=prospect_model.model_dump(),  # Convert to dict
        success=True
    )

def combine_structured(step_input: StepInput) -> StepOutput:
    print("\n" + "="*80)
    print("TESTING PYDANTIC MODEL SERIALIZATION IN PARALLEL BLOCKS")
    print("="*80)

    parallel_output = step_input.get_step_content("parallel_data")

    print(f"\nparallel_output type: {type(parallel_output)}")
    print(f"parallel_output keys: {parallel_output.keys()}")

    vendor_data = parallel_output["vendor"]
    prospect_data = parallel_output["prospect"]

    print(f"\n--- Vendor Data ---")
    print(f"Type: {type(vendor_data)}")
    print(f"Is VendorData instance? {isinstance(vendor_data, VendorData)}")
    print(f"Is dict? {isinstance(vendor_data, dict)}")
    print(f"Is string? {isinstance(vendor_data, str)}")
    print(f"Value preview: {str(vendor_data)[:150]}...")

    print(f"\n--- Prospect Data ---")
    print(f"Type: {type(prospect_data)}")
    print(f"Is ProspectData instance? {isinstance(prospect_data, ProspectData)}")
    print(f"Is dict? {isinstance(prospect_data, dict)}")
    print(f"Is string? {isinstance(prospect_data, str)}")
    print(f"Value preview: {str(prospect_data)[:150]}...")

    # Try to access as dict
    print(f"\n--- Attempting Dict Access ---")
    try:
        if isinstance(vendor_data, str):
            print("❌ vendor_data is STRING - needs ast.literal_eval() deserialization")
            import ast
            vendor_dict = ast.literal_eval(vendor_data)
            print(f"✅ After deserialization: {type(vendor_dict)}")
            print(f"✅ Can access domain: {vendor_dict['domain']}")
            print(f"✅ Can access offerings: {vendor_dict['offerings']}")
        elif isinstance(vendor_data, dict):
            print(f"✅ vendor_data is already dict, can access directly")
            print(f"✅ Domain: {vendor_data['domain']}")
            print(f"✅ Offerings: {vendor_data['offerings']}")
        else:
            print(f"❓ Unexpected type: {type(vendor_data)}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")

    return StepOutput(
        content=f"Vendor type: {type(vendor_data)}, Prospect type: {type(prospect_data)}",
        success=True
    )

# Create workflow
workflow = Workflow(
    name="Pydantic Serialization Test",
    steps=[
        Parallel(
            Step(name="vendor", executor=mock_vendor_step),
            Step(name="prospect", executor=mock_prospect_step),
            name="parallel_data"
        ),
        Step(name="combine", executor=combine_structured)
    ]
)

print("Running Pydantic serialization test...")
result = workflow.run(input={})

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("When StepOutput contains a Pydantic model.model_dump() (dict),")
print("Agno serializes it to a STRING when accessed from parallel blocks.")
print("This is why your helper function with ast.literal_eval() is essential!")
