# agents/agent_pipeline.py
from agents.search_agent    import SearchAgent
from agents.checklist_agent import ChecklistAgent
from agents.critic_agent    import CriticAgent

class AgentPipeline:
    """
    Orchestrates all 3 agents in sequence:
    Agent 1 (Search) → Agent 2 (Checklist) → Agent 3 (Critic)

    This replaces the old RunbookController + AIService direct calls
    in IncidentController.
    """

    def __init__(self):
        self.search_agent    = SearchAgent()
        self.checklist_agent = ChecklistAgent()
        self.critic_agent    = CriticAgent()

    def run(self, ticket):
        """
        Full pipeline execution.
        Input:  ticket dict { key, summary, description }
        Output: dict with everything IncidentController needs
        """
        print(f"\n{'='*50}")
        print(f"AGENT PIPELINE STARTED for ticket: {ticket['key']}")
        print(f"{'='*50}")

        # ── Agent 1 — Find the best matching runbook ──
        agent1_result = self.search_agent.run(ticket)

        # ── Agent 2 — Generate personalised checklist ──
        agent2_result = self.checklist_agent.run(agent1_result)

        # ── Agent 3 — Validate and add safety warnings ──
        agent3_result = self.critic_agent.run(agent2_result)

        print(f"\n{'='*50}")
        print(f"PIPELINE COMPLETE. Match: {agent1_result['match_type']}")
        print(f"{'='*50}\n")

        # Return everything the IncidentController needs
        return {
            'match_type':               agent1_result['match_type'],
            'matched_runbooks':         agent1_result['matched_runbooks'],
            'checklist_text':           agent3_result['validated_checklist_text'],
            'checklist_steps':          agent3_result['validated_steps'],
            'validation_summary':       agent3_result['validation_summary'],
            'changes_made':             agent3_result['changes_made'],
            'ticket':                   ticket
        }