# views/api_routes.py
from flask import Blueprint, request, jsonify
import traceback
from controllers.incident_controller import IncidentController
from models.runbook_model import RunbookModel
from services.ai_service import AIService

api = Blueprint('api', __name__)

# Initialize controllers
incident_controller = IncidentController()
runbook_model = RunbookModel()
ai_service = AIService()

@api.route('/process', methods=['POST'])
def process_ticket():
    """Process ticket endpoint"""
    print("\n" + "="*60)
    print("🎫 NEW REQUEST RECEIVED")
    print("="*60)
    
    try:
        data = request.json
        ticket_key = data.get('ticket_key', '').strip()
        
        if not ticket_key:
            return jsonify({
                'success': False,
                'error': 'Ticket key is required'
            }), 400
        
        print(f"🎟️  Processing: {ticket_key}")
        
        # Call controller
        result = incident_controller.process_incident(ticket_key)
        
        print(f"✅ Result: {result.get('success', False)}")
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/runbooks', methods=['GET'])
def list_runbooks():
    """List all runbooks"""
    try:
        runbooks = runbook_model.get_all_runbooks()
        return jsonify({
            'success': True,
            'runbooks': runbooks,
            'count': len(runbooks)
        })
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/create-runbook', methods=['POST'])
def create_runbook():
    """Create new runbook"""
    print("\n📝 CREATE RUNBOOK REQUEST")
    
    try:
        data = request.json
        
        title = data.get('title', '').strip()
        category = data.get('category', '').strip()
        keywords = data.get('keywords', '').strip()
        steps = data.get('steps', '').strip()
        
        if not all([title, category, keywords, steps]):
            return jsonify({
                'success': False,
                'error': 'All fields required: title, category, keywords, steps'
            }), 400
        
        runbook_id = runbook_model.create_runbook(title, category, keywords, steps)
        
        print(f"✅ Created runbook ID: {runbook_id}")
        
        return jsonify({
            'success': True,
            'message': 'Runbook created successfully',
            'runbook_id': runbook_id,
            'runbook': {
                'id': runbook_id,
                'title': title,
                'category': category,
                'keywords': keywords
            }
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/generate-runbook-draft', methods=['POST'])
def generate_draft():
    """Generate AI runbook draft"""
    print("\n🤖 GENERATE RUNBOOK DRAFT")
    
    try:
        data = request.json
        analysis = data.get('analysis', {})
        ticket = data.get('ticket', {})
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': 'Ticket data required'
            }), 400
        
        draft = ai_service.generate_runbook_draft(ticket, analysis)
        
        return jsonify({
            'success': True,
            'draft': draft
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'API is working!',
        'version': '2.0 MVC'
    })