from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import json

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sl@26062006',
    'database': 'healthmonitoring'
}

# Initialize ML model
model = RandomForestClassifier(n_estimators=50, random_state=42)

# Sample training data for common diseases in rural Northeast India
TRAINING_DATA = {
    'symptoms': [
        ['fever', 'headache', 'body_ache'], ['fever', 'chills', 'sweating'],
        ['cough', 'fever', 'chest_pain'], ['diarrhea', 'vomiting', 'dehydration'],
        ['fever', 'rash', 'joint_pain'], ['cough', 'shortness_breath', 'fatigue'],
        ['abdominal_pain', 'nausea', 'fever'], ['headache', 'neck_stiffness', 'fever'],
        ['skin_rash', 'itching', 'swelling'], ['chest_pain', 'difficulty_breathing', 'dizziness']
    ],
    'diseases': [
        'Malaria', 'Malaria', 'Pneumonia', 'Gastroenteritis', 'Dengue',
        'Tuberculosis', 'Typhoid', 'Meningitis', 'Allergic_Reaction', 'Heart_Disease'
    ]
}

# Disease information database
DISEASE_INFO = {
    'Malaria': {
        'first_aid': 'Keep patient hydrated, reduce fever with cool compress, seek immediate medical attention',
        'emergency': 'If severe symptoms like convulsions occur, rush to nearest hospital immediately',
        'prevention': 'Use mosquito nets, eliminate stagnant water, wear protective clothing',
        'awareness': 'Malaria is transmitted by mosquitoes. Early treatment is crucial for recovery.'
    },
    'Pneumonia': {
        'first_aid': 'Keep patient warm, encourage fluid intake, monitor breathing',
        'emergency': 'If breathing becomes very difficult, seek emergency medical care',
        'prevention': 'Get vaccinated, practice good hygiene, avoid smoking',
        'awareness': 'Pneumonia affects lungs and can be serious. Proper treatment is essential.'
    },
    'Gastroenteritis': {
        'first_aid': 'Provide oral rehydration solution, avoid solid foods initially',
        'emergency': 'If severe dehydration occurs, seek medical attention immediately',
        'prevention': 'Drink clean water, maintain food hygiene, wash hands frequently',
        'awareness': 'Usually caused by contaminated food or water. Hydration is key.'
    },
    'Dengue': {
        'first_aid': 'Rest, increase fluid intake, use paracetamol for fever (avoid aspirin)',
        'emergency': 'Watch for bleeding, severe abdominal pain - seek immediate care',
        'prevention': 'Eliminate mosquito breeding sites, use repellents',
        'awareness': 'Dengue is mosquito-borne. No specific treatment, supportive care is important.'
    },
    'Tuberculosis': {
        'first_aid': 'Ensure proper ventilation, encourage nutritious diet, rest',
        'emergency': 'If coughing blood or severe breathing difficulty, seek immediate care',
        'prevention': 'Maintain good nutrition, avoid crowded places, get tested regularly',
        'awareness': 'TB is curable with proper medication. Complete the full course of treatment.'
    }
}

def init_database():
    """Initialize database and create table if not exists"""
    try:
        # Connect without database to ensure DB exists
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS healthmonitoring")
        cursor.close()
        conn.close()

        # Reconnect with database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                symptoms TEXT,
                predicted_disease VARCHAR(100),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def train_model():
    """Train the ML model with sample data"""
    global model
    all_symptoms = set()
    for symptom_list in TRAINING_DATA['symptoms']:
        all_symptoms.update(symptom_list)
    symptom_list = list(all_symptoms)

    # Create feature vectors
    X = []
    for symptoms in TRAINING_DATA['symptoms']:
        feature_vector = [1 if symptom in symptoms else 0 for symptom in symptom_list]
        X.append(feature_vector)

    y = TRAINING_DATA['diseases']
    model.fit(X, y)
    return symptom_list

def predict_disease(symptoms):
    """Predict disease based on symptoms"""
    symptom_list = ['fever', 'headache', 'body_ache', 'chills', 'sweating', 'cough',
                   'chest_pain', 'diarrhea', 'vomiting', 'dehydration', 'rash',
                   'joint_pain', 'shortness_breath', 'fatigue', 'abdominal_pain',
                   'nausea', 'neck_stiffness', 'skin_rash', 'itching', 'swelling',
                   'difficulty_breathing', 'dizziness']
    feature_vector = [1 if symptom in symptoms else 0 for symptom in symptom_list]
    prediction = model.predict([feature_vector])[0]
    confidence = max(model.predict_proba([feature_vector])[0])
    return prediction, confidence

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        name = data.get('name', '')
        age = data.get('age', 0)
        symptoms = data.get('symptoms', [])

        predicted_disease, confidence = predict_disease(symptoms)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO health_records (name, age, symptoms, predicted_disease)
            VALUES (%s, %s, %s, %s)
        """, (name, age, json.dumps(symptoms), predicted_disease))
        conn.commit()
        cursor.close()
        conn.close()

        disease_info = DISEASE_INFO.get(predicted_disease, {
            'first_aid': 'Consult a healthcare professional for proper diagnosis and treatment',
            'emergency': 'If symptoms worsen, seek immediate medical attention',
            'prevention': 'Maintain good hygiene and healthy lifestyle',
            'awareness': 'Early detection and treatment are important for recovery'
        })

        return jsonify({
            'success': True,
            'predicted_disease': predicted_disease,
            'confidence': round(confidence * 100, 2),
            'disease_info': disease_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/records')
def get_records():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM health_records ORDER BY timestamp DESC LIMIT 10")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'records': records})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    if init_database():
        train_model()
        print("✅ Health Monitoring System initialized successfully!")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to initialize database. Please check MySQL connection.")
