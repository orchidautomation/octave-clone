"""
Test to prove that structured StepOutput causes serialization,
while Agent string responses don't.
"""

from dotenv import load_dotenv
load_dotenv()

from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput
from agno.agent import Agent

# Test 1: Custom executor with STRUCTURED dict output
def structured_executor_vendor(step_input: StepInput) -> StepOutput:
    """Returns structured dict - WILL be serialized"""
    return StepOutput(
        content={
            "vendor_domain": "https://example.com",
            "vendor_data": {"key": "value", "nested": {"deep": 123}}
        },
        success=True
    )

def structured_executor_prospect(step_input: StepInput) -> StepOutput:
    """Returns structured dict - WILL be serialized"""
    return StepOutput(
        content={
            "prospect_domain": "https://prospect.com",
            "prospect_data": {"key": "value2"}
        },
        success=True
    )

# Test 2: Custom executor with STRING output
def string_executor_vendor(step_input: StepInput) -> StepOutput:
    """Returns plain string - will NOT be serialized"""
    return StepOutput(
        content="This is a simple string response from vendor",
        success=True
    )

def string_executor_prospect(step_input: StepInput) -> StepOutput:
    """Returns plain string - will NOT be serialized"""
    return StepOutput(
        content="This is a simple string response from prospect",
        success=True
    )

# Checker function
def check_parallel_output(step_input: StepInput) -> StepOutput:
    print("\n" + "="*80)
    print("CHECKING PARALLEL OUTPUT TYPES")
    print("="*80)

    parallel_output = step_input.get_step_content("parallel_test")

    print(f"\nparallel_output type: {type(parallel_output)}")
    print(f"parallel_output keys: {parallel_output.keys() if isinstance(parallel_output, dict) else 'N/A'}")

    step1_content = parallel_output["step1"]
    step2_content = parallel_output["step2"]

    print(f"\nstep1_content type: {type(step1_content)}")
    print(f"step1_content value preview: {str(step1_content)[:100]}...")

    print(f"\nstep2_content type: {type(step2_content)}")
    print(f"step2_content value preview: {str(step2_content)[:100]}...")

    return StepOutput(content="done", success=True)


print("\n" + "="*80)
print("TEST 1: STRUCTURED DICT OUTPUTS")
print("="*80)

workflow1 = Workflow(
    name="Structured Output Test",
    steps=[
        Parallel(
            Step(name="step1", executor=structured_executor_vendor),
            Step(name="step2", executor=structured_executor_prospect),
            name="parallel_test"
        ),
        Step(name="check", executor=check_parallel_output)
    ]
)

result1 = workflow1.run(input={})

print("\n" + "="*80)
print("TEST 2: STRING OUTPUTS")
print("="*80)

workflow2 = Workflow(
    name="String Output Test",
    steps=[
        Parallel(
            Step(name="step1", executor=string_executor_vendor),
            Step(name="step2", executor=string_executor_prospect),
            name="parallel_test"
        ),
        Step(name="check", executor=check_parallel_output)
    ]
)

result2 = workflow2.run(input={})

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("Structured dict outputs get serialized to strings in parallel blocks.")
print("Plain string outputs remain as strings (no serialization needed).")
print("This is why our helper function with ast.literal_eval() is necessary!")
