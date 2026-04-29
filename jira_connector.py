import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv() 
jira = JIRA(
    server=os.getenv('JIRA_SERVER'),
    basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
)


ticket_key = 'AIM-1'  
issue = jira.issue(ticket_key)

print(f"Ticket: {issue.key}")
print(f"Summary: {issue.fields.summary}")
print(f"Description: {issue.fields.description}")
print(f"Status: {issue.fields.status.name}")
print(f"Priority: {issue.fields.priority.name}")