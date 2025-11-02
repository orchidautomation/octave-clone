"""
Phase 1 Tests
Unit tests for Step 1 (domain validation) and integration tests for Phase 1.
"""

import pytest
from agno.workflow.types import StepInput
from steps.step1_domain_validation import validate_vendor_domain, validate_prospect_domain


def test_step1_vendor_validation():
    """Test Step 1 vendor domain validation."""
    print("\n" + "=" * 60)
    print("TEST: Step 1 Vendor Domain Validation")
    print("=" * 60)

    # Create StepInput with vendor domain
    step_input = StepInput(
        input={"vendor_domain": "https://octavehq.com"}
    )

    # Run validator
    result = validate_vendor_domain(step_input)

    # Assertions
    assert result.success == True, "Vendor validation should succeed"
    assert "vendor_urls" in result.content, "Should return vendor_urls"
    assert "vendor_domain" in result.content, "Should return vendor_domain"
    assert "vendor_total_urls" in result.content, "Should return vendor_total_urls"
    assert len(result.content["vendor_urls"]) > 0, "Should discover at least some URLs"

    print(f"\n✅ Test passed!")
    print(f"   Domain: {result.content['vendor_domain']}")
    print(f"   URLs found: {result.content['vendor_total_urls']}")


def test_step1_prospect_validation():
    """Test Step 1 prospect domain validation."""
    print("\n" + "=" * 60)
    print("TEST: Step 1 Prospect Domain Validation")
    print("=" * 60)

    # Create StepInput with prospect domain
    step_input = StepInput(
        input={"prospect_domain": "https://sendoso.com"}
    )

    # Run validator
    result = validate_prospect_domain(step_input)

    # Assertions
    assert result.success == True, "Prospect validation should succeed"
    assert "prospect_urls" in result.content, "Should return prospect_urls"
    assert "prospect_domain" in result.content, "Should return prospect_domain"
    assert "prospect_total_urls" in result.content, "Should return prospect_total_urls"
    assert len(result.content["prospect_urls"]) > 0, "Should discover at least some URLs"

    print(f"\n✅ Test passed!")
    print(f"   Domain: {result.content['prospect_domain']}")
    print(f"   URLs found: {result.content['prospect_total_urls']}")


def test_step1_invalid_domain():
    """Test Step 1 with invalid domain."""
    print("\n" + "=" * 60)
    print("TEST: Step 1 Invalid Domain Handling")
    print("=" * 60)

    # Create StepInput with invalid domain (no protocol)
    step_input = StepInput(
        input={"vendor_domain": "octavehq.com"}  # Missing https://
    )

    # Run validator
    result = validate_vendor_domain(step_input)

    # Assertions
    assert result.success == False, "Should fail with invalid domain"
    assert result.stop == True, "Should stop workflow on invalid domain"
    assert "error" in result.content, "Should return error message"

    print(f"\n✅ Test passed!")
    print(f"   Error: {result.content['error']}")


def test_step1_missing_domain():
    """Test Step 1 with missing domain."""
    print("\n" + "=" * 60)
    print("TEST: Step 1 Missing Domain Handling")
    print("=" * 60)

    # Create StepInput without vendor_domain
    step_input = StepInput(
        input={}  # No vendor_domain
    )

    # Run validator
    result = validate_vendor_domain(step_input)

    # Assertions
    assert result.success == False, "Should fail with missing domain"
    assert result.stop == True, "Should stop workflow on missing domain"
    assert "error" in result.content, "Should return error message"

    print(f"\n✅ Test passed!")
    print(f"   Error: {result.content['error']}")


if __name__ == "__main__":
    """Run tests manually without pytest."""
    print("\n" + "=" * 60)
    print("RUNNING PHASE 1 TESTS")
    print("=" * 60)

    try:
        test_step1_vendor_validation()
        test_step1_prospect_validation()
        test_step1_invalid_domain()
        test_step1_missing_domain()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {str(e)}")
        print("=" * 60)
        raise
