"""
Step 3: Initial Analysis
Analyzes vendor and prospect homepages using AI.
Runs in parallel for both homepages.
"""

from agno.workflow.types import StepInput, StepOutput
from agents.homepage_analyst import homepage_analyst
from utils.workflow_helpers import safe_get_step_content, create_error_response, create_success_response


def analyze_vendor_homepage(step_input: StepInput) -> StepOutput:
    """
    Analyze vendor homepage with AI.

    Args:
        step_input: StepInput with access to Step 2 parallel_homepage_scraping output

    Returns:
        StepOutput with vendor homepage analysis
    """
    # Access parallel block by name first (per Agno docs)
    parallel_results = step_input.get_step_content("parallel_homepage_scraping")

    if not parallel_results or not isinstance(parallel_results, dict):
        return create_error_response("Step 2 parallel scraping failed: no results returned")

    # Extract individual step data from parallel results
    vendor_homepage_data = parallel_results.get("scrape_vendor_home")

    if not vendor_homepage_data:
        return create_error_response("Step 2 vendor scraping failed: no data returned")

    # Deserialize Python repr string if needed (Agno stores as str(dict))
    import ast
    if isinstance(vendor_homepage_data, str):
        try:
            vendor_homepage_data = ast.literal_eval(vendor_homepage_data)
        except (ValueError, SyntaxError) as e:
            return create_error_response(f"Step 2 vendor scraping failed: invalid data string - {str(e)}")

    if not isinstance(vendor_homepage_data, dict):
        return create_error_response(f"Step 2 vendor scraping failed: unexpected type {type(vendor_homepage_data)}")

    if "error" in vendor_homepage_data:
        return create_error_response(f"Step 2 vendor scraping failed: {vendor_homepage_data['error']}")

    markdown_content = vendor_homepage_data.get("vendor_homepage_markdown", "")

    if not markdown_content or len(markdown_content) < 100:
        return create_error_response("Vendor homepage content is too short or empty")

    print(f"🤖 Analyzing vendor homepage with AI...")

    try:
        # Run agent
        response = homepage_analyst.run(
            input=f"Analyze this homepage:\n\n{markdown_content}"
        )

        analysis = response.content

        print(f"✅ Vendor homepage analyzed")

        return create_success_response({
            "vendor_homepage_analysis": analysis
        })

    except Exception as e:
        return create_error_response(f"AI analysis failed: {str(e)}")


def analyze_prospect_homepage(step_input: StepInput) -> StepOutput:
    """
    Analyze prospect homepage with AI.

    Args:
        step_input: StepInput with access to Step 2 parallel_homepage_scraping output

    Returns:
        StepOutput with prospect homepage analysis
    """
    # Access parallel block by name first (per Agno docs)
    parallel_results = step_input.get_step_content("parallel_homepage_scraping")

    if not parallel_results or not isinstance(parallel_results, dict):
        return create_error_response("Step 2 parallel scraping failed: no results returned")

    # Extract individual step data from parallel results
    prospect_homepage_data = parallel_results.get("scrape_prospect_home")

    if not prospect_homepage_data:
        return create_error_response("Step 2 prospect scraping failed: no data returned")

    # Deserialize Python repr string if needed (Agno stores as str(dict))
    import ast
    if isinstance(prospect_homepage_data, str):
        try:
            prospect_homepage_data = ast.literal_eval(prospect_homepage_data)
        except (ValueError, SyntaxError) as e:
            return create_error_response(f"Step 2 prospect scraping failed: invalid data string - {str(e)}")

    if not isinstance(prospect_homepage_data, dict):
        return create_error_response(f"Step 2 prospect scraping failed: unexpected type {type(prospect_homepage_data)}")

    if "error" in prospect_homepage_data:
        return create_error_response(f"Step 2 prospect scraping failed: {prospect_homepage_data['error']}")

    markdown_content = prospect_homepage_data.get("prospect_homepage_markdown", "")

    if not markdown_content or len(markdown_content) < 100:
        return create_error_response("Prospect homepage content is too short or empty")

    print(f"🤖 Analyzing prospect homepage with AI...")

    try:
        # Run agent
        response = homepage_analyst.run(
            input=f"Analyze this homepage:\n\n{markdown_content}"
        )

        analysis = response.content

        print(f"✅ Prospect homepage analyzed")

        return create_success_response({
            "prospect_homepage_analysis": analysis
        })

    except Exception as e:
        return create_error_response(f"AI analysis failed: {str(e)}")
