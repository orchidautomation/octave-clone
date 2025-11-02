"""
Step 4: URL Prioritization
Selects the most valuable URLs to scrape from both vendor and prospect websites.
Sequential step (runs after parallel homepage analysis).
"""

from agno.workflow.types import StepInput, StepOutput
from agents.url_prioritizer import url_prioritizer
from utils.workflow_helpers import safe_get_step_content, create_error_response, create_success_response


def prioritize_urls(step_input: StepInput) -> StepOutput:
    """
    Prioritize URLs from both companies using AI.

    Args:
        step_input: StepInput with access to Step 1 outputs (validate_vendor, validate_prospect)

    Returns:
        StepOutput with selected URLs for both companies
    """
    # Get URLs from Step 1 - access parallel block first (per Agno docs)
    parallel_results = step_input.get_step_content("parallel_validation")

    if not parallel_results or not isinstance(parallel_results, dict):
        return create_error_response("Step 1 parallel validation failed: no results returned")

    # Extract individual step data from parallel results
    vendor_data = parallel_results.get("validate_vendor")
    prospect_data = parallel_results.get("validate_prospect")

    # Deserialize Python repr strings if needed (Agno stores as str(dict))
    import ast
    if isinstance(vendor_data, str):
        try:
            vendor_data = ast.literal_eval(vendor_data)
        except (ValueError, SyntaxError) as e:
            return create_error_response(f"Vendor validation failed: invalid data string - {str(e)}")

    if isinstance(prospect_data, str):
        try:
            prospect_data = ast.literal_eval(prospect_data)
        except (ValueError, SyntaxError) as e:
            return create_error_response(f"Prospect validation failed: invalid data string - {str(e)}")

    if not vendor_data or not isinstance(vendor_data, dict):
        return create_error_response("Vendor validation failed: no data")

    if "error" in vendor_data:
        return create_error_response(f"Vendor validation failed: {vendor_data['error']}")

    if not prospect_data or not isinstance(prospect_data, dict):
        return create_error_response("Prospect validation failed: no data")

    if "error" in prospect_data:
        return create_error_response(f"Prospect validation failed: {prospect_data['error']}")

    vendor_urls = vendor_data.get("vendor_urls", [])
    prospect_urls = prospect_data.get("prospect_urls", [])

    if not vendor_urls or not prospect_urls:
        return create_error_response("No URLs found from Step 1 validation")

    print(f"🎯 Prioritizing {len(vendor_urls)} vendor URLs and {len(prospect_urls)} prospect URLs...")

    # Prepare input for agent (limit to first 200 URLs to avoid token overflow)
    prompt = f"""
VENDOR URLs ({len(vendor_urls)} total):
{chr(10).join(vendor_urls[:200])}

PROSPECT URLs ({len(prospect_urls)} total):
{chr(10).join(prospect_urls[:200])}

Select the top 10-15 most valuable URLs from each company for sales intelligence gathering.
"""

    try:
        # Run agent
        response = url_prioritizer.run(input=prompt)

        result = response.content

        # Extract URLs from structured output
        vendor_selected = [item.url for item in result.vendor_selected_urls]
        prospect_selected = [item.url for item in result.prospect_selected_urls]

        print(f"✅ Selected {len(vendor_selected)} vendor URLs and {len(prospect_selected)} prospect URLs")

        return create_success_response({
            "vendor_selected_urls": vendor_selected,
            "prospect_selected_urls": prospect_selected,
            "vendor_url_details": [item.dict() for item in result.vendor_selected_urls],
            "prospect_url_details": [item.dict() for item in result.prospect_selected_urls]
        })

    except Exception as e:
        return create_error_response(f"URL prioritization failed: {str(e)}")
