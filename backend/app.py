from flask import Flask, jsonify
from flask_cors import CORS
from views.api_routes import api
from config import Config

app = Flask(__name__)
CORS(app)

# Register blueprint BEFORE app.run()
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({
        'status': 'OK',
        'message': 'AI Incident Management - MVC Architecture',
        'version': '2.0',
        'endpoints': [
            '/api/process',
            '/api/runbooks',
            '/api/create-runbook',
            '/api/generate-runbook-draft',
            '/api/test'
        ]
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AI INCIDENT MANAGEMENT - MVC ARCHITECTURE")
    print("="*60)
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )