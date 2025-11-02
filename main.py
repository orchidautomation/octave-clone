"""
Octave Clone MVP - Main Entry Point
CLI for running the Phase 1 intelligence gathering workflow.

Usage:
    python main.py <vendor_domain> <prospect_domain>

Example:
    python main.py https://octavehq.com https://sendoso.com
"""

import sys
import json
from datetime import datetime
from workflow import phase1_workflow


def main():
    """Main entry point for Phase 1 workflow."""

    # Parse command line arguments
    if len(sys.argv) < 3:
        print("=" * 80)
        print("OCTAVE CLONE MVP - PHASE 1")
        print("=" * 80)
        print("\nUsage: python main.py <vendor_domain> <prospect_domain>")
        print("\nExample:")
        print("  python main.py https://octavehq.com https://sendoso.com")
        print("\n" + "=" * 80)
        sys.exit(1)

    vendor_domain = sys.argv[1]
    prospect_domain = sys.argv[2]

    # Display header
    print("=" * 80)
    print("OCTAVE CLONE MVP - PHASE 1: INTELLIGENCE GATHERING")
    print("=" * 80)
    print(f"\n📊 Vendor:   {vendor_domain}")
    print(f"🎯 Prospect: {prospect_domain}\n")
    print("=" * 80)
    print("\n🚀 Starting Phase 1 workflow...\n")

    # Prepare workflow input
    workflow_input = {
        "vendor_domain": vendor_domain,
        "prospect_domain": prospect_domain
    }

    try:
        # Run workflow
        result = phase1_workflow.run(input=workflow_input)

        # Check if workflow was successful
        if not result or not result.content:
            print("\n" + "=" * 80)
            print("❌ WORKFLOW FAILED")
            print("=" * 80)
            print("\nNo result returned from workflow.")
            sys.exit(1)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"phase1_output_{timestamp}.json"

        with open(output_filename, "w") as f:
            json.dump(result.content, f, indent=2)

        # Display success message
        print("\n" + "=" * 80)
        print("✅ PHASE 1 COMPLETE!")
        print("=" * 80)

        # Print summary
        content = result.content
        print(f"\n📄 Results saved to: {output_filename}\n")
        print("📊 Summary:")
        print(f"   • Vendor URLs scraped: {len(content.get('vendor_content', {}))} pages")
        print(f"   • Prospect URLs scraped: {len(content.get('prospect_content', {}))} pages")

        # Display stats if available
        stats = content.get('stats', {})
        if stats:
            print(f"   • Vendor content: {stats.get('vendor_chars', 0):,} characters")
            print(f"   • Prospect content: {stats.get('prospect_chars', 0):,} characters")

        print("\n" + "=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ WORKFLOW ERROR")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        print("\nPlease check your API keys in .env and try again.")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
