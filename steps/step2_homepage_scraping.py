"""
Step 2: Homepage Scraping
Scrapes vendor and prospect homepages.
Runs in parallel for both homepages.
"""

from agno.workflow.types import StepInput, StepOutput
from utils.firecrawl_helpers import scrape_url
from utils.workflow_helpers import safe_get_step_content, create_error_response, create_success_response


def scrape_vendor_homepage(step_input: StepInput) -> StepOutput:
    """
    Scrape vendor homepage.

    Args:
        step_input: StepInput with access to Step 1 validate_vendor output

    Returns:
        StepOutput with vendor homepage content (markdown, html, metadata)
    """
    # Access parallel block by name first (per Agno docs)
    parallel_results = step_input.get_step_content("parallel_validation")

    if not parallel_results or not isinstance(parallel_results, dict):
        return create_error_response("Step 1 parallel validation failed: no results returned")

    # Extract individual step data from parallel results
    vendor_data = parallel_results.get("validate_vendor")

    if not vendor_data:
        return create_error_response("Step 1 vendor validation failed: no data returned")

    # Deserialize Python repr string if needed (Agno stores as str(dict))
    import ast
    if isinstance(vendor_data, str):
        try:
            vendor_data = ast.literal_eval(vendor_data)
        except (ValueError, SyntaxError) as e:
            return create_error_response(f"Step 1 vendor validation failed: invalid data string - {str(e)}")

    # vendor_data should be a dict with vendor_domain, vendor_urls, etc.
    if not isinstance(vendor_data, dict):
        return create_error_response(f"Step 1 vendor validation failed: unexpected type {type(vendor_data)}")

    if "error" in vendor_data:
        return create_error_response(f"Step 1 vendor validation failed: {vendor_data['error']}")

    vendor_domain = vendor_data.get("vendor_domain")
    if not vendor_domain:
        return create_error_response("Step 1 vendor validation failed: no vendor_domain in data")

    print(f"📄 Scraping vendor homepage: {vendor_domain}")
    result = scrape_url(vendor_domain, formats=['markdown', 'html'])

    if not result["success"]:
        error_msg = f"Failed to scrape vendor homepage: {result.get('error', 'Unknown error')}"
        return create_error_response(error_msg)

    print(f"✅ Scraped vendor homepage ({len(result['markdown'])} chars)")

    return create_success_response({
        "vendor_domain": vendor_domain,
        "vendor_homepage_markdown": result["markdown"],
        "vendor_homepage_html": result["html"],
        "vendor_homepage_metadata": result["metadata"]
    })


def scrape_prospect_homepage(step_input: StepInput) -> StepOutput:
    """
    Scrape prospect homepage.

    Args:
        step_input: StepInput with access to Step 1 validate_prospect output

    Returns:
        StepOutput with prospect homepage content (markdown, html, metadata)
    """
    # Access parallel block by name first (per Agno docs)
    parallel_results = step_input.get_step_content("parallel_validation")

    if not parallel_results or not isinstance(parallel_results, dict):
        return create_error_response("Step 1 parallel validation failed: no results returned")

    # Extract individual step data from parallel results
    prospect_data = parallel_results.get("validate_prospect")

    if not prospect_data:
        return create_error_response("Step 1 prospect validation failed: no data returned")

    # Deserialize Python repr string if needed (Agno stores as str(dict))
    import ast
    if isinstance(prospect_data, str):
        try:
            prospect_data = ast.literal_eval(prospect_data)
        except (ValueError, SyntaxError) as e:
            return create_error_response(f"Step 1 prospect validation failed: invalid data string - {str(e)}")

    if not isinstance(prospect_data, dict):
        return create_error_response(f"Step 1 prospect validation failed: unexpected type {type(prospect_data)}")

    if "error" in prospect_data:
        return create_error_response(f"Step 1 prospect validation failed: {prospect_data['error']}")

    prospect_domain = prospect_data.get("prospect_domain")
    if not prospect_domain:
        return create_error_response("Step 1 prospect validation failed: no prospect_domain in data")

    print(f"📄 Scraping prospect homepage: {prospect_domain}")
    result = scrape_url(prospect_domain, formats=['markdown', 'html'])

    if not result["success"]:
        error_msg = f"Failed to scrape prospect homepage: {result.get('error', 'Unknown error')}"
        return create_error_response(error_msg)

    print(f"✅ Scraped prospect homepage ({len(result['markdown'])} chars)")

    return create_success_response({
        "prospect_domain": prospect_domain,
        "prospect_homepage_markdown": result["markdown"],
        "prospect_homepage_html": result["html"],
        "prospect_homepage_metadata": result["metadata"]
    })
