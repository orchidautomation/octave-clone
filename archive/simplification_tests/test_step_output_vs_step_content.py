"""
Test get_step_output() vs get_step_content() for custom executors
This could simplify the workflow even further!
"""

from dotenv import load_dotenv
load_dotenv()

from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput

# Custom executor with structured dict output
def vendor_executor(step_input: StepInput) -> StepOutput:
    """Returns structured dict - let's see if get_step_output() preserves it"""
    return StepOutput(
        content={
            "vendor_domain": "https://example.com",
            "vendor_data": {"key": "value", "nested": {"deep": 123}}
        },
        success=True
    )

def prospect_executor(step_input: StepInput) -> StepOutput:
    """Returns structured dict"""
    return StepOutput(
        content={
            "prospect_domain": "https://prospect.com",
            "prospect_data": {"key": "value2"}
        },
        success=True
    )

# Test both methods
def compare_methods(step_input: StepInput) -> StepOutput:
    print("\n" + "="*80)
    print("COMPARING get_step_content() vs get_step_output()")
    print("="*80)

    # Method 1: get_step_content() (what we've been using)
    print("\n--- Method 1: get_step_content() ---")
    try:
        content_output = step_input.get_step_content("parallel_test")
        print(f"Type: {type(content_output)}")
        print(f"Keys: {content_output.keys() if isinstance(content_output, dict) else 'N/A'}")

        vendor_content = content_output["step1"]
        print(f"\nvendor_content type: {type(vendor_content)}")
        print(f"Is dict? {isinstance(vendor_content, dict)}")
        print(f"Is string? {isinstance(vendor_content, str)}")

        if isinstance(vendor_content, str):
            print("❌ Returns STRING - needs deserialization")
        else:
            print("✅ Returns DICT - no deserialization needed")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")

    # Method 2: get_step_output() (the new discovery!)
    print("\n--- Method 2: get_step_output() ---")
    try:
        output_output = step_input.get_step_output("parallel_test")
        print(f"Type: {type(output_output)}")

        # StepOutput has a .content attribute, let's check what's in there
        if hasattr(output_output, 'content'):
            print(f"output_output.content type: {type(output_output.content)}")
            print(f"output_output.content keys: {output_output.content.keys() if isinstance(output_output.content, dict) else 'N/A'}")

            if isinstance(output_output.content, dict):
                # Try accessing the parallel step results from content
                vendor_data = output_output.content.get("step1")
                print(f"\nvendor_data type: {type(vendor_data)}")
                print(f"Is dict? {isinstance(vendor_data, dict)}")
                print(f"Is string? {isinstance(vendor_data, str)}")

                if isinstance(vendor_data, dict):
                    print("✅ Returns DICT directly - no deserialization needed!")
                    print(f"✅ Can access: {vendor_data.get('vendor_domain')}")
                else:
                    print("❌ Returns STRING - needs deserialization")

        # Check the .steps attribute - this might contain the parallel step outputs!
        if hasattr(output_output, 'steps') and output_output.steps:
            print(f"\n✨ output_output.steps exists!")
            print(f"Type: {type(output_output.steps)}")
            print(f"Length: {len(output_output.steps) if isinstance(output_output.steps, list) else 'N/A'}")

            if isinstance(output_output.steps, list):
                # Iterate through the list
                for idx, step in enumerate(output_output.steps):
                    print(f"\n--- Step {idx} ---")
                    print(f"Type: {type(step)}")

                    if hasattr(step, 'step_name'):
                        print(f"step_name: {step.step_name}")

                    if hasattr(step, 'content'):
                        print(f"content type: {type(step.content)}")
                        print(f"Is dict? {isinstance(step.content, dict)}")

                        if isinstance(step.content, dict):
                            print("✅✅ Returns DICT directly - NO DESERIALIZATION NEEDED!")
                            print(f"✅ Content keys: {step.content.keys()}")
                            print(f"✅ Sample value: {list(step.content.values())[0]}")
                        else:
                            print(f"❌ Still a string: {str(step.content)[:100]}...")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")

    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)

    return StepOutput(content="done", success=True)

# Create workflow
workflow = Workflow(
    name="Method Comparison Test",
    steps=[
        Parallel(
            Step(name="step1", executor=vendor_executor),
            Step(name="step2", executor=prospect_executor),
            name="parallel_test"
        ),
        Step(name="compare", executor=compare_methods)
    ]
)

print("Testing get_step_output() vs get_step_content()...")
result = workflow.run(input={})
