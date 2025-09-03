import os
import sys
import sqlite3
import base64
import io
import json
from datetime import datetime
import numpy as np
from PIL import Image
# cv2 removed for lightweight deployment
from flask import Flask, render_template, request, jsonify

# TensorFlow import - graceful handling for deployment
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("TensorFlow not available - using fallback mood prediction")
from flask_cors import CORS

# Add the parent directory to the Python path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# Configuration
DATABASE = '../mood_history.db'
MODEL_PATH = '../models/mood_classifier.h5'
CANVAS_SIZE = 224  # Standard CNN input size

# Music mapping - demo track names (actual files excluded for deployment size)
MOOD_MUSIC_MAP = {
    'happy': {
        'tracks': ['Happy Melody', 'Joyful Tune', 'Upbeat Rhythm'],
        'color': '#FFD700',
        'description': 'Upbeat and joyful vibes!'
    },
    'calm': {
        'tracks': ['Peaceful Sounds', 'Relaxing Waves', 'Gentle Breeze'],
        'color': '#87CEEB',
        'description': 'Peaceful and relaxing sounds'
    },
    'sad': {
        'tracks': ['Melancholy', 'Soft Reflection', 'Gentle Rain'],
        'color': '#696969',
        'description': 'Melancholic and introspective'
    },
    'energetic': {
        'tracks': ['High Energy Beat', 'Pump Up', 'Motivation Mix'],
        'color': '#FF4500',
        'description': 'High energy and motivation!'
    }
}

def get_database_path():
    """Get the correct database path for Vercel deployment"""
    if os.environ.get('VERCEL'):
        # On Vercel, use /tmp directory for SQLite
        return '/tmp/mood_history.db'
    else:
        # Local development
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mood_history.db')

def init_database():
    """Initialize SQLite database for mood history"""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            predicted_mood TEXT,
            confidence REAL,
            user_feedback INTEGER,
            image_data TEXT
        )
    ''')
    conn.commit()
    conn.close()


def preprocess_image(image_data):
    """Preprocess canvas image for CNN input"""
    try:
        # Decode base64 image
        image_data = image_data.split(',')[1]  # Remove data:image/png;base64,
        image_bytes = base64.b64decode(image_data)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert('L')  # Grayscale
        
        # Resize to model input size
        image = image.resize((CANVAS_SIZE, CANVAS_SIZE))
        
        # Convert to numpy array and normalize
        image_array = np.array(image) / 255.0
        
        # Add batch and channel dimensions
        image_array = image_array.reshape(1, CANVAS_SIZE, CANVAS_SIZE, 1)
        
        return image_array
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def predict_mood_fallback(image_array):
    """Fallback mood prediction based on basic image features"""
    # Simple heuristic based on drawing density and patterns
    image_2d = image_array[0, :, :, 0]
    
    # Calculate features
    total_pixels = np.sum(image_2d < 0.9)  # Non-white pixels
    density = total_pixels / (CANVAS_SIZE * CANVAS_SIZE)
    
    # Simple gradient-based complexity (replaces OpenCV edge detection)
    grad_x = np.abs(np.diff(image_2d, axis=1))
    grad_y = np.abs(np.diff(image_2d, axis=0))
    complexity = (np.sum(grad_x > 0.1) + np.sum(grad_y > 0.1)) / (CANVAS_SIZE * CANVAS_SIZE)
    
    # Simple rule-based classification
    if density > 0.3 and complexity > 0.1:
        return 'energetic', 0.75
    elif density < 0.1:
        return 'calm', 0.65
    elif complexity < 0.05:
        return 'sad', 0.60
    else:
        return 'happy', 0.70

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return jsonify({'status': 'working', 'message': 'API is functional'})

@app.route('/predict_mood', methods=['POST'])
def predict_mood():
    print(f"Received request to /predict_mood")
    try:
        # Check if request has JSON data
        if not request.is_json:
            print("Request is not JSON")
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        if data is None:
            print("No JSON data received")
            return jsonify({'error': 'No JSON data provided'}), 400
            
        print(f"Received data keys: {list(data.keys()) if data else 'None'}")
        
        image_data = data.get('image')
        if not image_data:
            print("No image data in request")
            return jsonify({'error': 'No image data provided'}), 400
        
        print(f"Image data length: {len(image_data)}")
        
        # Preprocess image
        processed_image = preprocess_image(image_data)
        if processed_image is None:
            print("Failed to preprocess image")
            return jsonify({'error': 'Failed to process image'}), 400
        
        print("Image preprocessing successful")
        
        # Use fallback method for lightweight deployment
        predicted_mood, confidence = predict_mood_fallback(processed_image)
        print(f"Predicted mood: {predicted_mood} with confidence: {confidence}")
        
        # Get music recommendations
        music_data = MOOD_MUSIC_MAP.get(predicted_mood, MOOD_MUSIC_MAP['happy'])
        
        # Save to database
        try:
            db_path = get_database_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO mood_history (timestamp, predicted_mood, confidence, image_data)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now(), predicted_mood, confidence, image_data[:100]))  # Limit image data size for storage
            conn.commit()
            history_id = cursor.lastrowid
            conn.close()
            print(f"Saved to database with ID: {history_id}")
        except Exception as db_error:
            print(f"Database error: {db_error}")
            history_id = None  # Continue without saving to DB
        
        response = {
            'mood': predicted_mood,
            'confidence': confidence,
            'music': music_data,
            'history_id': history_id
        }
        print(f"Returning response: {response}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in predict_mood: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        history_id = data.get('history_id')
        rating = data.get('rating')  # 1-5 scale
        
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE mood_history SET user_feedback = ? WHERE id = ?
        ''', (rating, history_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error in submit_feedback: {e}")
        return jsonify({'error': 'Failed to save feedback'}), 500

@app.route('/history')
def get_history():
    try:
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, predicted_mood, confidence, user_feedback
            FROM mood_history
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'timestamp': row[1],
                'mood': row[2],
                'confidence': row[3],
                'feedback': row[4]
            })
        
        return jsonify({'history': history})
        
    except Exception as e:
        print(f"Error in get_history: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

@app.route('/export_csv')
def export_csv():
    try:
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, predicted_mood, confidence, user_feedback
            FROM mood_history
            ORDER BY timestamp DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        
        # Create CSV content
        csv_content = "Timestamp,Mood,Confidence,User_Rating\n"
        for row in results:
            csv_content += f"{row[0]},{row[1]},{row[2]},{row[3] or 'N/A'}\n"
        
        return csv_content, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=mood_history.csv'
        }
        
    except Exception as e:
        print(f"Error in export_csv: {e}")
        return jsonify({'error': 'Failed to export data'}), 500

# Initialize database on startup
init_database()

# This is important for Vercel
if __name__ == '__main__':
    app.run(debug=True)
