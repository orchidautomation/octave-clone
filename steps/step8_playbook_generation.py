"""
Step 8: Playbook Generation
Transforms vendor + prospect intelligence into actionable sales playbooks
"""

from agno.workflow.types import StepInput, StepOutput
from agents.playbook_specialists.playbook_orchestrator import playbook_orchestrator
from agents.playbook_specialists.email_sequence_writer import email_sequence_writer
from agents.playbook_specialists.talk_track_creator import talk_track_creator
from agents.playbook_specialists.battle_card_builder import battle_card_builder
from utils.workflow_helpers import get_parallel_step_content, create_error_response, create_success_response
import json
from datetime import datetime


def generate_playbook_summary(step_input: StepInput) -> StepOutput:
    """
    Step 8a: Generate executive summary and identify priority personas

    This step runs AFTER Phases 1-3 complete, and synthesizes all intelligence
    into a strategic playbook summary.
    """
    try:
        # Get vendor intelligence from Step 6 (vendor_element_extraction Parallel block)
        offerings_data = get_parallel_step_content(step_input, "vendor_element_extraction", "extract_offerings")
        case_studies_data = get_parallel_step_content(step_input, "vendor_element_extraction", "extract_case_studies")
        value_props_data = get_parallel_step_content(step_input, "vendor_element_extraction", "extract_value_props")
        use_cases_data = get_parallel_step_content(step_input, "vendor_element_extraction", "extract_use_cases")
        personas_data = get_parallel_step_content(step_input, "vendor_element_extraction", "extract_personas")
        differentiators_data = get_parallel_step_content(step_input, "vendor_element_extraction", "extract_differentiators")
        proof_points_data = get_parallel_step_content(step_input, "vendor_element_extraction", "extract_proof_points")
        customers_data = get_parallel_step_content(step_input, "vendor_element_extraction", "extract_customers")

        if not offerings_data:
            return create_error_response("No vendor extraction results available")

        # Access each vendor extraction result directly
        vendor_intel = {
            "offerings": offerings_data.get("offerings", []),
            "case_studies": case_studies_data.get("case_studies", []) if case_studies_data else [],
            "value_propositions": value_props_data.get("value_propositions", []) if value_props_data else [],
            "use_cases": use_cases_data.get("use_cases", []) if use_cases_data else [],
            "target_personas": personas_data.get("target_personas", []) if personas_data else [],
            "differentiators": differentiators_data.get("differentiators", []) if differentiators_data else [],
            "proof_points": proof_points_data.get("proof_points", []) if proof_points_data else [],
            "customers": customers_data.get("reference_customers", []) if customers_data else []
        }

        # Get prospect buyer personas from Step 7b
        prospect_personas_data = step_input.get_step_content("identify_buyer_personas")
        if not prospect_personas_data:
            return create_error_response("No buyer personas identified")

        target_personas = prospect_personas_data.get("target_buyer_personas", [])

        # Get prospect context from Step 7a (prospect_context_analysis Parallel block)
        company_data = get_parallel_step_content(step_input, "prospect_context_analysis", "analyze_company")
        pain_points_data = get_parallel_step_content(step_input, "prospect_context_analysis", "analyze_pain_points")

        prospect_intel = {
            "company_profile": company_data.get("company_profile", {}) if company_data else {},
            "pain_points": pain_points_data.get("pain_points", []) if pain_points_data else [],
            "target_buyer_personas": target_personas
        }

        print(f"\n📋 Generating playbook executive summary...")
        print(f"   Vendor elements: {sum(len(v) if isinstance(v, list) else 0 for v in vendor_intel.values())} items")
        print(f"   Prospect personas: {len(target_personas)}")

        # Build prompt
        vendor_name = vendor_intel.get("offerings", [{}])[0].get("name", "the vendor") if vendor_intel.get("offerings") else "the vendor"
        prospect_name = prospect_intel["company_profile"].get("company_name", "the prospect company")

        prompt = f"""
VENDOR INTELLIGENCE:
{json.dumps(vendor_intel, indent=2)}

PROSPECT INTELLIGENCE:
{json.dumps(prospect_intel, indent=2)}

TASK:
Create a strategic executive summary for the sales playbook.

This playbook will help sales reps at {vendor_name} engage with {prospect_name}.

Provide:
1. Executive summary (2-3 paragraphs)
2. Priority personas (ordered list of titles)
3. Top 5 quick wins for sales team
4. Success metrics to track
"""

        # Run orchestrator
        response = playbook_orchestrator.run(input=prompt)

        summary_data = response.content
        print(f"✅ Playbook summary generated")
        print(f"   Priority personas: {', '.join(summary_data.priority_personas)}")

        return StepOutput(
            content={
                "executive_summary": summary_data.executive_summary,
                "priority_personas": summary_data.priority_personas,
                "quick_wins": summary_data.quick_wins,
                "success_metrics": summary_data.success_metrics,
                "vendor_intelligence": vendor_intel,
                "prospect_intelligence": prospect_intel
            },
            success=True
        )

    except Exception as e:
        print(f"❌ Error generating playbook summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return StepOutput(
            content={"error": str(e)},
            success=False
        )


def generate_email_sequences(step_input: StepInput) -> StepOutput:
    """
    Step 8b: Generate 4-touch email sequences for top 3 personas
    """
    try:
        # Get playbook summary from Step 8a
        summary = step_input.get_step_content("generate_playbook_summary")

        if not summary or not summary.get("priority_personas"):
            return StepOutput(
                content={"error": "No playbook summary available", "email_sequences": []},
                success=False
            )

        priority_personas = summary["priority_personas"][:3]  # Top 3
        vendor_intel = summary["vendor_intelligence"]
        prospect_intel = summary["prospect_intelligence"]

        # Find full persona data
        all_personas = prospect_intel["target_buyer_personas"]

        sequences = []

        for persona_title in priority_personas:
            # Find matching persona
            persona_data = next(
                (p for p in all_personas if p["persona_title"] == persona_title),
                None
            )

            if not persona_data:
                print(f"⚠️  Persona data not found for {persona_title}")
                continue

            print(f"✉️  Generating 4-touch email sequence for {persona_title}...")

            prompt = f"""
TARGET PERSONA:
{json.dumps(persona_data, indent=2)}

VENDOR INTELLIGENCE:
{json.dumps(vendor_intel, indent=2)}

PROSPECT CONTEXT:
Company: {prospect_intel['company_profile'].get('company_name')}
Industry: {prospect_intel['company_profile'].get('industry')}
Pain Points: {json.dumps(prospect_intel['pain_points'], indent=2)}

TASK:
Create a 4-touch email sequence over 14 days for this persona.
Follow the pain→value→follow-up→breakup framework.
Day 1, Day 3, Day 7, Day 14.
"""

            response = email_sequence_writer.run(input=prompt)
            sequences.extend(response.content.email_sequences)

            seq_count = len(response.content.email_sequences)
            print(f"   ✅ {seq_count} sequence(s) created")

        print(f"✅ Total email sequences generated: {len(sequences)}")

        return StepOutput(
            content={"email_sequences": [seq.model_dump() for seq in sequences]},
            success=True
        )

    except Exception as e:
        print(f"❌ Error generating email sequences: {str(e)}")
        import traceback
        traceback.print_exc()
        return StepOutput(
            content={"error": str(e), "email_sequences": []},
            success=False
        )


def generate_talk_tracks(step_input: StepInput) -> StepOutput:
    """
    Step 8c: Generate talk tracks for top 3 personas
    """
    try:
        summary = step_input.get_step_content("generate_playbook_summary")

        if not summary:
            return StepOutput(
                content={"error": "No playbook summary", "talk_tracks": []},
                success=False
            )

        priority_personas = summary["priority_personas"][:3]
        vendor_intel = summary["vendor_intelligence"]
        prospect_intel = summary["prospect_intelligence"]
        all_personas = prospect_intel["target_buyer_personas"]

        talk_tracks = []

        for persona_title in priority_personas:
            persona_data = next(
                (p for p in all_personas if p["persona_title"] == persona_title),
                None
            )

            if not persona_data:
                continue

            print(f"🎯 Generating talk tracks for {persona_title}...")

            prompt = f"""
TARGET PERSONA:
{json.dumps(persona_data, indent=2)}

VENDOR INTELLIGENCE:
{json.dumps(vendor_intel, indent=2)}

PROSPECT CONTEXT:
{json.dumps(prospect_intel, indent=2)}

TASK:
Create comprehensive talk tracks for this persona including:
- Elevator pitch (30 seconds)
- Cold call script
- Discovery call script
- Demo talking points
- Value mapping (connect vendor capabilities to persona pain points)
"""

            response = talk_track_creator.run(input=prompt)
            talk_tracks.extend(response.content.talk_tracks)

            print(f"   ✅ Talk track created")

        print(f"✅ Total talk tracks generated: {len(talk_tracks)}")

        return StepOutput(
            content={"talk_tracks": [tt.model_dump() for tt in talk_tracks]},
            success=True
        )

    except Exception as e:
        print(f"❌ Error generating talk tracks: {str(e)}")
        import traceback
        traceback.print_exc()
        return StepOutput(
            content={"error": str(e), "talk_tracks": []},
            success=False
        )


def generate_battle_cards(step_input: StepInput) -> StepOutput:
    """
    Step 8d: Generate battle cards (objection handling, competitive positioning)
    """
    try:
        summary = step_input.get_step_content("generate_playbook_summary")

        if not summary:
            return StepOutput(
                content={"error": "No playbook summary", "battle_cards": []},
                success=False
            )

        vendor_intel = summary["vendor_intelligence"]
        prospect_intel = summary["prospect_intelligence"]

        print(f"⚔️  Generating battle cards...")

        prompt = f"""
VENDOR INTELLIGENCE:
{json.dumps(vendor_intel, indent=2)}

PROSPECT INTELLIGENCE:
{json.dumps(prospect_intel, indent=2)}

TASK:
Create battle cards for the sales team:
1. Why We Win battle card
2. Objection Handling battle card (7-10 common objections)
3. Competitive Positioning (vs. manual/in-house solutions or competitors if intel available)

Use Fact-Impact-Act framework.
Be specific and actionable.
Include exact talk tracks.
"""

        response = battle_card_builder.run(input=prompt)
        battle_cards = response.content.battle_cards

        print(f"✅ {len(battle_cards)} battle cards generated")
        for card in battle_cards:
            print(f"   - {card.title} ({card.card_type})")

        return StepOutput(
            content={"battle_cards": [bc.model_dump() for bc in battle_cards]},
            success=True
        )

    except Exception as e:
        print(f"❌ Error generating battle cards: {str(e)}")
        import traceback
        traceback.print_exc()
        return StepOutput(
            content={"error": str(e), "battle_cards": []},
            success=False
        )


def assemble_final_playbook(step_input: StepInput) -> StepOutput:
    """
    Step 8e: Assemble all playbook components into final deliverable
    """
    try:
        # Get all playbook components from Step 8 parallel block
        email_sequences_data = get_parallel_step_content(step_input, "playbook_component_generation", "generate_email_sequences")
        talk_tracks_data = get_parallel_step_content(step_input, "playbook_component_generation", "generate_talk_tracks")
        battle_cards_data = get_parallel_step_content(step_input, "playbook_component_generation", "generate_battle_cards")

        if not email_sequences_data and not talk_tracks_data and not battle_cards_data:
            return create_error_response("No playbook components available")

        # Get summary (sequential step before parallel)
        summary = step_input.get_step_content("generate_playbook_summary")

        # Get vendor/prospect names
        vendor_name = summary["vendor_intelligence"]["offerings"][0]["name"] if summary["vendor_intelligence"].get("offerings") else "Vendor"
        prospect_name = summary["prospect_intelligence"]["company_profile"].get("company_name", "Prospect")

        # Assemble final playbook
        final_playbook = {
            "vendor_name": vendor_name,
            "prospect_name": prospect_name,
            "generated_date": datetime.now().strftime("%Y-%m-%d"),

            # From summary
            "executive_summary": summary["executive_summary"],
            "priority_personas": summary["priority_personas"],
            "quick_wins": summary["quick_wins"],
            "success_metrics": summary["success_metrics"],

            # From parallel specialists
            "email_sequences": email_sequences_data.get("email_sequences", []) if email_sequences_data else [],
            "talk_tracks": talk_tracks_data.get("talk_tracks", []) if talk_tracks_data else [],
            "battle_cards": battle_cards_data.get("battle_cards", []) if battle_cards_data else []
        }

        print(f"\n🎉 PLAYBOOK GENERATION COMPLETE!")
        print(f"=" * 60)
        print(f"Vendor: {vendor_name}")
        print(f"Prospect: {prospect_name}")
        print(f"Generated: {final_playbook['generated_date']}")
        print(f"")
        print(f"📊 Playbook Contents:")
        print(f"   • Executive Summary: ✓")
        print(f"   • Priority Personas: {len(final_playbook['priority_personas'])}")
        print(f"   • Email Sequences: {len(final_playbook['email_sequences'])}")
        print(f"   • Talk Tracks: {len(final_playbook['talk_tracks'])}")
        print(f"   • Battle Cards: {len(final_playbook['battle_cards'])}")
        print(f"   • Quick Wins: {len(final_playbook['quick_wins'])}")
        print(f"=" * 60)

        return StepOutput(
            content={"sales_playbook": final_playbook},
            success=True
        )

    except Exception as e:
        print(f"❌ Error assembling final playbook: {str(e)}")
        import traceback
        traceback.print_exc()
        return StepOutput(
            content={"error": str(e)},
            success=False
        )
