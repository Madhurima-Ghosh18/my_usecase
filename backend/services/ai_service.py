# services/ai_service.py
import re
from huggingface_hub import InferenceClient
from config import Config

class AIService:
    """AI/LLM service for analysis and generation"""
    
    def __init__(self):
        self.client = InferenceClient(
            model=Config.MODEL_NAME,
            token=Config.HUGGINGFACE_API_KEY
        )
    
    def analyze_incident_type(self, ticket):
        """AI analyzes ticket to determine incident type"""
        messages = [{
            "role": "user",
            "content": f"""Analyze this incident and identify its type and category.

Incident Summary: {ticket['summary']}
Description: {ticket['description'][:600]}

Provide analysis in this EXACT format:
INCIDENT_TYPE: [specific type, e.g. Email Delivery Failure]
CATEGORY: [single word, e.g. email, frontend, database]
KEYWORDS: [10-15 specific keywords from the description]
CONFIDENCE: [High/Medium/Low]

Be specific — use actual technology names from the description."""
        }]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=200,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            analysis = self._parse_analysis(analysis_text)
            
            print(f"   Type: {analysis['incident_type']}")
            print(f"   Category: {analysis['category']}")
            
            return analysis
            
        except Exception as e:
            print(f"   ⚠️ Analysis failed: {e}")
            return self._fallback_analysis(ticket)
    
    def _parse_analysis(self, text):
        """Parse AI analysis response"""
        analysis = {
            'incident_type': 'Unknown Issue',
            'category': 'general',
            'keywords': 'incident,issue,problem',
            'confidence': 'Low'
        }
        
        for line in text.split('\n'):
            if 'INCIDENT_TYPE:' in line:
                analysis['incident_type'] = line.split('INCIDENT_TYPE:')[1].strip()
            elif 'CATEGORY:' in line:
                analysis['category'] = line.split('CATEGORY:')[1].strip().lower()
            elif 'KEYWORDS:' in line:
                analysis['keywords'] = line.split('KEYWORDS:')[1].strip()
            elif 'CONFIDENCE:' in line:
                analysis['confidence'] = line.split('CONFIDENCE:')[1].strip()
        
        return analysis
    
    def _fallback_analysis(self, ticket):
        """Fallback analysis when AI fails"""
        stop_words = {'the','a','an','is','are','was','were','be','been','have','has',
                      'had','do','does','did','will','would','could','should','not','no',
                      'and','or','but','in','on','at','by','for','with','to','of','from',
                      'that','this','it','its','users','user','cannot','can','application',
                      'app','service','issue','problem','error','failing','failed'}
        
        combined = f"{ticket['summary']} {ticket['description'][:300]}".lower()
        words = re.findall(r'\b[a-z]{3,}\b', combined)
        meaningful = list(dict.fromkeys([w for w in words if w not in stop_words]))
        
        return {
            'incident_type': ticket['summary'],
            'category': meaningful[0] if meaningful else 'general',
            'keywords': ','.join(meaningful[:15]),
            'confidence': 'Low'
        }
    
    def generate_generic_steps(self, ticket, analysis):
        """Generate troubleshooting steps for unknown incident types"""
        messages = [{
            "role": "user",
            "content": f"""Generate troubleshooting steps for this specific incident.

Incident: {ticket['summary']}
Description: {ticket['description'][:600]}
Type: {analysis['incident_type']}
Category: {analysis['category']}

Generate 10-15 numbered steps with commands, expected results, and actions.
Steps must be specific to THIS incident type."""
        }]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=1000,
                temperature=0.4
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"   ⚠️ Generic steps generation failed: {e}")
            return self._fallback_generic_steps(ticket, analysis)
    
    def _fallback_generic_steps(self, ticket, analysis):
        """Fallback generic steps when AI fails"""
        category = analysis['category']
        incident_type = analysis['incident_type']
        
        return f"""1. Verify scope of {incident_type}
Check: Confirm how many users/services are affected
Action: Document affected scope before proceeding

2. Check {category} service logs
Command: tail -f /var/log/{category}/application.log
Look for: Error messages matching {incident_type}

3. Check recent changes
Command: git log --since="24 hours ago" --oneline
Action: Consider rollback if change correlates with incident

4. Verify credentials and configuration
Check: API keys, passwords, endpoints for {category} service
Action: Rotate or fix any invalid credentials found

5. Check resource usage
Command: top -b -n 1 | head -20
Action: Address resource constraints if found

6. Attempt service restart
Command: sudo systemctl restart {category}-service
Expected: Service restarts within 30 seconds

7. Validate fix
Command: curl http://localhost/health
Expected: Healthy status restored

8. Monitor post-fix
Command: watch -n 5 'systemctl status {category}-service'
Action: Monitor for at least 15 minutes

9. Document root cause
Action: Record exact cause and fix applied

10. Create permanent runbook
Action: Create a runbook based on these steps"""
    
    def generate_checklist(self, runbook, ticket):
        """Generate detailed checklist from runbook"""
        steps_preview = runbook['steps'][:2000]
        
        messages = [{
            "role": "user",
            "content": f"""Create a detailed checklist for this incident.

Incident: {ticket['summary']}
Runbook: {runbook['title']}
Steps: {steps_preview}

Format as numbered steps with commands and expected results."""
        }]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=1500,
                temperature=0.3
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"   ⚠️ Checklist generation failed: {e}")
            return runbook['steps']
    
    def generate_solution_summary(self, runbook, ticket):
        """Generate one-line solution summary"""
        messages = [{
            "role": "user",
            "content": f"""Provide ONE concise solution sentence.

Incident: {ticket['summary']}
Runbook: {runbook['title']}

One sentence, 15 words or less."""
        }]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=30,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Follow {runbook['title']} runbook to resolve the issue"
    
    def generate_runbook_draft(self, ticket, analysis):
        """Generate complete runbook draft from ticket"""
        ticket_summary = ticket.get('summary', '')
        ticket_description = str(ticket.get('description', ''))[:800]
        
        messages = [{
            "role": "user",
            "content": f"""Create a detailed runbook for this incident.

Ticket Summary: {ticket_summary}
Ticket Description: {ticket_description}

Provide metadata in EXACT format:
TITLE: [specific title using actual service/technology name]
CATEGORY: [single word]
KEYWORDS: [15 comma-separated keywords from ticket]

Then generate 15 numbered troubleshooting steps with commands."""
        }]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=2000,
                temperature=0.3
            )
            return self._parse_runbook_draft(response.choices[0].message.content, ticket, analysis)
            
        except Exception as e:
            print(f"⚠️ Draft generation failed: {e}")
            return self._fallback_runbook_draft(ticket, analysis)
    
    def _parse_runbook_draft(self, response_text, ticket, analysis):
        """Parse AI-generated runbook draft"""
        suggested_title = f"{ticket['summary']} Resolution"
        suggested_category = analysis.get('category', 'general')
        suggested_keywords = analysis.get('keywords', 'incident,issue,problem')
        
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('TITLE:'):
                val = line.split('TITLE:')[1].strip()
                if val and 'Unknown' not in val:
                    suggested_title = val
            elif line.startswith('CATEGORY:'):
                val = line.split('CATEGORY:')[1].strip().lower()
                if val and val != 'general':
                    suggested_category = val
            elif line.startswith('KEYWORDS:'):
                val = line.split('KEYWORDS:')[1].strip()
                if val:
                    suggested_keywords = val
        
        draft_steps = '\n'.join([
            line for line in response_text.split('\n')
            if not line.strip().startswith(('TITLE:', 'CATEGORY:', 'KEYWORDS:'))
        ]).strip()
        
        return {
            'title': suggested_title,
            'category': suggested_category,
            'keywords': suggested_keywords,
            'steps': draft_steps
        }
    
    def _fallback_runbook_draft(self, ticket, analysis):
        """Fallback runbook draft when AI fails"""
        stop_words = {'the','a','an','is','are','was','were','be','been','have','has',
                      'had','do','does','did','will','would','could','should','not','no',
                      'and','or','but','in','on','at','by','for','with','to','of','from',
                      'that','this','it','its','users','user','cannot','can','application',
                      'app','service','issue','problem','error','failing','failed'}
        
        combined = f"{ticket['summary']} {ticket['description'][:500]}".lower()
        words = re.findall(r'\b[a-z]{3,}\b', combined)
        meaningful = list(dict.fromkeys([w for w in words if w not in stop_words]))
        
        category = meaningful[0] if meaningful else 'general'
        
        return {
            'title': f"{ticket['summary']} Resolution",
            'category': category,
            'keywords': ','.join(meaningful[:15]),
            'steps': f"""1. Verify scope of incident
2. Check service logs
3. Review recent changes
4. Check external dependencies
5. Verify credentials
6. Check resource usage
7. Attempt service restart
8. Validate fix
9. Monitor post-fix
10. Document root cause"""
        }