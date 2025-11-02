"""
Test to verify Agno's data serialization behavior.

This test proves whether Agno returns step outputs as:
1. Dicts (expected) - no deserialization needed
2. Strings (unexpected) - deserialization required

If test shows dicts are returned directly, we can remove 40+ lines
of ast.literal_eval() code from 6 files.
"""

from agno.workflow import Workflow, Step, StepInput, StepOutput


def step1_returns_complex_dict(step_input: StepInput) -> StepOutput:
    """
    Step 1: Returns a complex nested dictionary.
    This simulates what your validation steps return.
    """
    complex_data = {
        "vendor_domain": "example.com",
        "vendor_urls": ["https://example.com/page1", "https://example.com/page2"],
        "nested": {
            "key": "value",
            "number": 123,
            "list": [1, 2, 3]
        },
        "items": [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"}
        ]
    }

    print("✅ Step 1: Returning complex dict")
    return StepOutput(
        content=complex_data,
        success=True
    )


def step2_reads_previous(step_input: StepInput) -> StepOutput:
    """
    Step 2: Reads previous step output and checks type.
    This proves whether deserialization is needed.
    """
    print("\n" + "="*60)
    print("TESTING AGNO SERIALIZATION BEHAVIOR")
    print("="*60)

    # Get previous step content
    previous = step_input.previous_step_content

    # Check type
    print(f"\n📊 Type of previous_step_content: {type(previous)}")
    print(f"📊 Is dict? {isinstance(previous, dict)}")
    print(f"📊 Is string? {isinstance(previous, str)}")

    # Try direct dict access
    if isinstance(previous, dict):
        print("\n✅ SUCCESS: Content is already a dict!")
        print("   → No deserialization needed")
        print("   → Can remove all ast.literal_eval() code")

        # Test nested access
        vendor_domain = previous.get("vendor_domain")
        nested_value = previous.get("nested", {}).get("key")
        first_item = previous.get("items", [{}])[0].get("name") if previous.get("items") else None

        print(f"\n📝 Direct access works:")
        print(f"   - vendor_domain: {vendor_domain}")
        print(f"   - nested.key: {nested_value}")
        print(f"   - items[0].name: {first_item}")

        result = "PASS"

    elif isinstance(previous, str):
        print("\n❌ UNEXPECTED: Content is a string")
        print("   → Deserialization IS needed")
        print("   → Keep ast.literal_eval() code")

        # Try deserialization
        import ast
        try:
            deserialized = ast.literal_eval(previous)
            print(f"   → Deserialized successfully to: {type(deserialized)}")
            result = "FAIL"
        except Exception as e:
            print(f"   → Deserialization failed: {e}")
            result = "ERROR"
    else:
        print(f"\n⚠️  UNEXPECTED TYPE: {type(previous)}")
        result = "ERROR"

    print("\n" + "="*60)
    print(f"TEST RESULT: {result}")
    print("="*60 + "\n")

    return StepOutput(
        content={
            "test_result": result,
            "content_type": str(type(previous)),
            "is_dict": isinstance(previous, dict)
        },
        success=True
    )


# Create simple test workflow
print("\n" + "🧪 CREATING TEST WORKFLOW" + "\n")

test_workflow = Workflow(
    name="Serialization Test",
    steps=[
        Step(name="return_complex_dict", executor=step1_returns_complex_dict),
        Step(name="test_type", executor=step2_reads_previous)
    ]
)

# Run the test
print("🚀 RUNNING TEST...\n")
test_workflow.print_response("test_input")

print("\n" + "="*60)
print("TEST COMPLETE - Check output above for results")
print("="*60)
