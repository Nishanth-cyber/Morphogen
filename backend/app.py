"""
Flask API Server for Generative Design System
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from config import Config
from pipeline import GenerativeDesignPipeline

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize pipeline
pipeline = GenerativeDesignPipeline()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Generative Design API is running"
    })


@app.route('/api/generate', methods=['POST'])
def generate_floorplan():
    """
    Main endpoint to generate floor plan
    
    Request body:
    {
        "user_input": "Build me a 2-bedroom house"
    }
    
    Response:
    {
        "success": true,
        "filename": "floorplan_20250126_143022.lsp",
        "autolisp_code": "...",
        "metadata": {...}
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'user_input' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'user_input' in request body"
            }), 400
        
        user_input = data['user_input'].strip()
        
        if not user_input:
            return jsonify({
                "success": False,
                "error": "user_input cannot be empty"
            }), 400
        
        # Execute pipeline
        result = pipeline.execute(user_input)
        
        if result['success']:
            return jsonify({
                "success": True,
                "filename": result['filename'],
                "autolisp_code": result['autolisp_code'],
                "metadata": {
                    "building_type": result['metadata']['intent'].get('building_type'),
                    "bedroom_count": result['metadata']['intent'].get('bedroom_count'),
                    "total_area": result['metadata']['requirements'].get('total_area_sqft'),
                    "rooms": [r['name'] for r in result['metadata']['requirements'].get('rooms', [])]
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download generated .lsp file
    
    GET /api/download/floorplan_20250126_143022.lsp
    """
    try:
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                "success": False,
                "error": "File not found"
            }), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    """
    List all generated .lsp files
    
    GET /api/files
    """
    try:
        files = []
        for filename in os.listdir(Config.OUTPUT_DIR):
            if filename.endswith('.lsp'):
                filepath = os.path.join(Config.OUTPUT_DIR, filename)
                file_info = {
                    "filename": filename,
                    "size": os.path.getsize(filepath),
                    "created": os.path.getctime(filepath)
                }
                files.append(file_info)
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            "success": True,
            "files": files
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("GENERATIVE DESIGN API SERVER")
    print("="*60)
    print(f"Server starting at http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"Output directory: {Config.OUTPUT_DIR}")
    print("="*60 + "\n")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )
