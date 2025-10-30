# Smart Community Health Monitoring System

## Setup Instructions

1. Install Python dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

2. Setup MySQL database:
   - Install MySQL server
   - Create database: `CREATE DATABASE health_monitoring;`
   - Update DB_CONFIG in app.py with your credentials

3. Run the application:
   \`\`\`
   python app.py
   \`\`\`

4. Access the system at: http://localhost:5000

## Features
- Symptom-based disease prediction
- Immediate first aid guidance
- Emergency guidelines
- Prevention measures
- Health awareness tips
- Data storage for tracking

## Database Schema
- Table: health_records
- Columns: id, name, age, symptoms, predicted_disease, timestamp
