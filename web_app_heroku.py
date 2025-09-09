#!/usr/bin/env python3
"""
Web-based Bubble Drawing Tool - Heroku Version

A Flask web application optimized for Heroku deployment.

Author: Manus AI
"""

import os
import uuid
import zipfile
from datetime import datetime
from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import logging

# Import our bubble drawing tool
from improved_bubble_tool import ImprovedBubbleDrawingTool

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bubble drawing tool
bubble_tool = ImprovedBubbleDrawingTool()

def allowed_file(filename):
    """Check if the uploaded file is a PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Generate unique ID for this processing job
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
        file.save(input_path)
        
        # Create output directory for this job
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Get processing mode from form
        use_manual = request.form.get('mode') == 'manual'
        
        # Process the PDF
        logger.info(f"Processing job {job_id}: {filename}")
        success = bubble_tool.process_pdf_improved(input_path, output_dir, use_manual)
        
        if success:
            # Create a zip file with all results
            zip_path = os.path.join(output_dir, 'results.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file != 'results.zip':  # Don't include the zip in itself
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, output_dir)
                            zipf.write(file_path, arcname)
            
            # Clean up input file
            os.remove(input_path)
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'message': 'Processing completed successfully!'
            })
        else:
            return jsonify({'error': 'Processing failed'}), 500
            
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/download/<job_id>')
def download_results(job_id):
    """Download the results zip file."""
    try:
        zip_path = os.path.join(app.config['OUTPUT_FOLDER'], job_id, 'results.zip')
        if os.path.exists(zip_path):
            return send_file(zip_path, as_attachment=True, download_name=f'bubble_results_{job_id}.zip')
        else:
            return "Results not found", 404
    except Exception as e:
        logger.error(f"Error downloading results: {e}")
        return "Download error", 500

@app.route('/status/<job_id>')
def job_status(job_id):
    """Check the status of a processing job."""
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
    zip_path = os.path.join(output_dir, 'results.zip')
    
    if os.path.exists(zip_path):
        return jsonify({'status': 'completed', 'download_url': url_for('download_results', job_id=job_id)})
    elif os.path.exists(output_dir):
        return jsonify({'status': 'processing'})
    else:
        return jsonify({'status': 'not_found'}), 404

@app.route('/demo')
def demo():
    """Demo page with sample drawings."""
    return render_template('demo.html')

@app.route('/api/demo/process')
def demo_process():
    """Process the demo drawing."""
    try:
        # Use the test drawing we created earlier
        demo_pdf_path = 'test_drawing.pdf'
        if not os.path.exists(demo_pdf_path):
            return jsonify({'error': 'Demo file not found'}), 404
        
        # Generate unique ID for demo
        job_id = f"demo_{str(uuid.uuid4())[:8]}"
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Process with manual mode for demo
        success = bubble_tool.process_pdf_improved(demo_pdf_path, output_dir, use_manual=True)
        
        if success:
            # Create zip file
            zip_path = os.path.join(output_dir, 'results.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file != 'results.zip':
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, output_dir)
                            zipf.write(file_path, arcname)
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'download_url': url_for('download_results', job_id=job_id)
            })
        else:
            return jsonify({'error': 'Demo processing failed'}), 500
            
    except Exception as e:
        logger.error(f"Demo processing error: {e}")
        return jsonify({'error': f'Demo error: {str(e)}'}), 500

if __name__ == '__main__':
    # Use PORT environment variable for Heroku
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

