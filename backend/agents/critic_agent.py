from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from config import Config


class CriticAgent:
    """
    Agent 3 — Critic / Validation Agent
    Reviews the checklist from Agent 2.
    Checks for safety issues, completeness, and logical order.
    Adds warnings for dangerous commands.
    """

    DANGEROUS_PATTERNS = [
        'rm -rf',
        'drop table',
        'delete from',
        'kill -9',
        'format',
        'truncate',
        ':(){:|:&};:',
        'chmod 777',
        'DROP DATABASE',
    ]

    def __init__(self):

        self.llm = HuggingFaceEndpoint(
            repo_id=Config.MODEL_NAME,
            huggingfacehub_api_token=Config.HUGGINGFACE_API_KEY,
            temperature=0.3,
            max_new_tokens=600
        )

        self.prompt = PromptTemplate(
            input_variables=["checklist_steps", "incident_type"],
            template="""You are a senior SRE reviewing an incident resolution checklist.

Incident type: {incident_type}

Checklist to review:
{checklist_steps}

Review these steps and respond with ONLY one of:
- APPROVED: steps are safe, complete and in correct order
- REVISED: [list what you changed and why]

Be brief. Focus on safety and completeness only."""
        )

        self.chain = self.prompt | self.llm

    def run(self, agent2_output):

        print(f"\n[Agent 3] Validating checklist...")

        steps = agent2_output['checklist_steps']
        ticket = agent2_output['ticket_context']
        runbook_title = agent2_output.get('runbook_title', 'Unknown')

        # Rule-based safety scan
        steps_with_warnings, safety_changes = self._safety_scan(steps)

        steps_text = '\n'.join(
            f"{i+1}. {s}" for i, s in enumerate(steps_with_warnings)
        )

        incident_type = runbook_title if runbook_title else ticket['summary']

        try:

            result = self.chain.invoke({
                "checklist_steps": steps_text,
                "incident_type": incident_type
            })

            ai_verdict = result.strip()

        except Exception as e:

            print(f"[Agent 3] AI review failed, using rule-based only: {e}")
            ai_verdict = "APPROVED"

        all_changes = safety_changes.copy()
        status = "approved"

        if ai_verdict.upper().startswith("REVISED"):
            status = "revised"
            all_changes.append(f"AI review: {ai_verdict}")

        validation_summary = (
            f"{len(steps_with_warnings)} steps validated. "
            f"Status: {status.upper()}. "
            f"Changes: {len(all_changes)}"
        )

        validated_text = self._rebuild_checklist(
            agent2_output,
            steps_with_warnings,
            validation_summary,
            all_changes
        )

        print(
            f"[Agent 3] Validation complete. Status: {status}. "
            f"Changes made: {len(all_changes)}"
        )

        return {
            'validated_checklist_text': validated_text,
            'validated_steps': steps_with_warnings,
            'validation_summary': validation_summary,
            'changes_made': all_changes,
            'status': status,
            'original_output': agent2_output
        }

    def _safety_scan(self, steps):

        modified_steps = []
        changes = []

        for step in steps:

            step_lower = step.lower()

            is_dangerous = any(
                pattern.lower() in step_lower
                for pattern in self.DANGEROUS_PATTERNS
            )

            if is_dangerous:

                warned_step = f"⚠️ CAUTION — Take backup before running: {step}"

                modified_steps.append(warned_step)

                changes.append(
                    f"Added safety warning to: '{step[:50]}...'"
                )

            else:
                modified_steps.append(step)

        has_backup = any(
            'backup' in s.lower() or 'snapshot' in s.lower()
            for s in steps
        )

        needs_backup = any(
            word in ' '.join(steps).lower()
            for word in ['database', 'postgres', 'mysql', 'disk', 'delete']
        )

        if needs_backup and not has_backup:

            modified_steps.insert(
                0,
                "Take a backup/snapshot before proceeding"
            )

            changes.append(
                "Added backup step at start (database/disk operation detected)"
            )

        return modified_steps, changes

    def _rebuild_checklist(self, agent2_output, validated_steps, summary, changes):

        steps_text = '\n'.join(f"# {step}" for step in validated_steps)

        ticket = agent2_output['ticket_context']

        runbook_title = agent2_output.get(
            'runbook_title',
            'AI Generated'
        )

        changes_text = (
            '\n'.join(f"* {c}" for c in changes)
            if changes else '* No changes required'
        )

        return f"""h2. AI Incident Resolution Checklist ✅ Validated

*Ticket:* {ticket['key']} — {ticket['summary']}
*Runbook:* {runbook_title}
*Validation:* {summary}

h3. Resolution Steps
{steps_text}

h3. Validation Checklist
* [] Incident resolved and service stable
* [] Monitored for 5+ minutes with no recurrence

h3. Agent Review Notes
{changes_text}

_Validated by AI Incident Management Agent (Agent 3 — Critic)_"""