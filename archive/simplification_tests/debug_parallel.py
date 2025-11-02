"""
Debug script to see what parallel blocks actually contain
"""

from agno.workflow import Workflow, Step, Parallel, StepInput, StepOutput
from steps.step1_domain_validation import validate_vendor_domain, validate_prospect_domain


def debug_step2(step_input: StepInput) -> StepOutput:
    """Debug step to inspect parallel block contents"""
    print("\n" + "="*80)
    print("DEBUG STEP 2: INSPECTING PARALLEL VALIDATION")
    print("="*80)

    # Get the parallel validation block
    parallel_validation = step_input.get_step_content("parallel_validation")

    print(f"\nparallel_validation type: {type(parallel_validation)}")
    print(f"parallel_validation value: {parallel_validation}")

    if isinstance(parallel_validation, dict):
        print(f"\nKeys in parallel_validation: {parallel_validation.keys()}")
        for key, value in parallel_validation.items():
            print(f"\n{key}:")
            print(f"  Type: {type(value)}")
            if isinstance(value, dict):
                print(f"  Keys: {value.keys()}")
            print(f"  Value: {value}")
    elif isinstance(parallel_validation, str):
        print("\n❌ PROBLEM: parallel_validation is a STRING!")
        print(f"String value: {parallel_validation}")

    return StepOutput(content={"debug": "complete"})


# Create workflow with step 1 and debug step 2
debug_workflow = Workflow(
    name="Debug Parallel Blocks",
    steps=[
        Parallel(
            Step(name="validate_vendor", executor=validate_vendor_domain),
            Step(name="validate_prospect", executor=validate_prospect_domain),
            name="parallel_validation"
        ),
        Step(name="debug_step2", executor=debug_step2)
    ]
)

# Run with test input
workflow_input = {
    "vendor_domain": "https://octavehq.com",
    "prospect_domain": "https://sendoso.com"
}

print("Running workflow with Step 1 + Debug Step 2...")
result = debug_workflow.run(input=workflow_input)

print("\n" + "="*80)
print("DEBUG COMPLETE")
print("="*80)
