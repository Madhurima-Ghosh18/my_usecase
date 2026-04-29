# services/jira_service.py
from jira import JIRA
from jira.exceptions import JIRAError
from config import Config

class JiraService:
    """Jira API integration service"""
    
    def __init__(self):
        self.server = Config.JIRA_SERVER
        self.email = Config.JIRA_EMAIL
        self.api_token = Config.JIRA_API_TOKEN
    
    def get_client(self):
        """Get authenticated Jira client"""
        return JIRA(
            server=self.server,
            basic_auth=(self.email, self.api_token)
        )
    
    def get_ticket(self, ticket_key):
        """Fetch ticket from Jira with error handling"""
        try:
            jira = self.get_client()
            issue = jira.issue(ticket_key)
            return {
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': issue.fields.description or "No description provided"
            }
        except JIRAError as e:
            if e.status_code == 404:
                raise ValueError(f"Ticket '{ticket_key}' does not exist or you don't have permission to view it.")
            elif e.status_code == 401:
                raise ValueError("Authentication failed. Please check your Jira credentials in .env file.")
            elif e.status_code == 403:
                raise ValueError(f"You don't have permission to access ticket '{ticket_key}'.")
            else:
                raise ValueError(f"Jira error: {str(e)}")
    
    def post_comment(self, ticket_key, comment):
        """Post comment to Jira ticket"""
        try:
            jira = self.get_client()
            jira.add_comment(ticket_key, comment)
            print(f"✓ Posted comment to {ticket_key}")
            return True
        except JIRAError as e:
            print(f"⚠️ Failed to post comment to Jira: {e}")
            return False