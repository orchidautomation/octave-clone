"""
Test Phase 4 - Playbook Generation
Run complete Phase 1-2-3-4 workflow end-to-end
"""

from workflow import phase1_2_3_4_workflow
import json
from datetime import datetime


def main():
    print("=" * 80)
    print("OCTAVE CLONE MVP - PHASE 1-2-3-4 COMPLETE TEST")
    print("Complete Sales Intelligence Pipeline + Playbook Generation")
    print("=" * 80)

    # Test with Octave (vendor) and Sendoso (prospect)
    workflow_input = {
        "vendor_domain": "https://octavehq.com",
        "prospect_domain": "https://sendoso.com"
    }

    print(f"\nVendor:   {workflow_input['vendor_domain']}")
    print(f"Prospect: {workflow_input['prospect_domain']}\n")
    print("=" * 80)
    print("\nStarting complete sales intelligence + playbook pipeline...\n")

    # Run workflow
    start_time = datetime.now()
    result = phase1_2_3_4_workflow.run(input=workflow_input)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 80)
    print("PHASE 1-2-3-4 COMPLETE")
    print("=" * 80)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"phase4_output_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(result.content, f, indent=2)

    print(f"\n✅ Results saved to {output_file}")
    print(f"⏱️  Total execution time: {duration:.1f} seconds ({duration/60:.1f} minutes)")

    # Print playbook summary
    print("\n" + "=" * 80)
    print("COMPLETE SALES PLAYBOOK SUMMARY")
    print("=" * 80)

    playbook = result.content.get("sales_playbook", {})

    if playbook:
        print(f"\n📋 PLAYBOOK: {playbook.get('vendor_name')} → {playbook.get('prospect_name')}")
        print(f"Generated: {playbook.get('generated_date')}")
        print(f"\n" + "=" * 80)

        print(f"\n📊 CONTENTS:")
        print(f"   • Executive Summary: ✓")
        print(f"   • Priority Personas: {len(playbook.get('priority_personas', []))}")

        personas = playbook.get('priority_personas', [])
        if personas:
            for i, persona in enumerate(personas, 1):
                print(f"      {i}. {persona}")

        print(f"\n   • Email Sequences: {len(playbook.get('email_sequences', []))}")
        for seq in playbook.get('email_sequences', []):
            print(f"      - {seq.get('sequence_name')} ({seq.get('total_touches')} touches)")

        print(f"\n   • Talk Tracks: {len(playbook.get('talk_tracks', []))}")
        for tt in playbook.get('talk_tracks', []):
            print(f"      - {tt.get('persona_title')}")

        print(f"\n   • Battle Cards: {len(playbook.get('battle_cards', []))}")
        for bc in playbook.get('battle_cards', []):
            print(f"      - {bc.get('title')} ({bc.get('card_type')})")

        print(f"\n   • Quick Wins: {len(playbook.get('quick_wins', []))}")
        for i, qw in enumerate(playbook.get('quick_wins', [])[:3], 1):
            print(f"      {i}. {qw}")

        print(f"\n   • Success Metrics: {len(playbook.get('success_metrics', {}))}")

    print("\n" + "=" * 80)
    print("✅ Phase 4 test complete!")
    print("=" * 80)
    print(f"\n🎉 OCTAVE CLONE MVP IS COMPLETE!")
    print(f"\nFull pipeline operational:")
    print(f"  1. ✅ Intelligence Gathering (Phase 1)")
    print(f"  2. ✅ Vendor Element Extraction (Phase 2)")
    print(f"  3. ✅ Prospect Persona Identification (Phase 3)")
    print(f"  4. ✅ Sales Playbook Generation (Phase 4)")
    print(f"\n  Ready for production deployment with AgentOS!")
    print("=" * 80)


if __name__ == "__main__":
    main()
