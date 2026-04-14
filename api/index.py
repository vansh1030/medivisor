import os
import joblib
from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client

# Initialize Flask App
# We adjust the folder paths so it can find them correctly regardless of execution directory.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'templates'), 
            static_folder=os.path.join(base_dir, 'static'))

# Load Model
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model.pkl')
model = None
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    print("Warning: Model not found at", model_path)

# Initialize Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print("Error initializing Supabase client:", e)

# Treatments configuration
TREATMENTS = {
    "Low": {
        "advice": "Your asthma risk profile appears to be low. Continue healthy habits and regular check-ups.",
        "disclaimer": "This is a predicted assessment. Consult a doctor for professional advice."
    },
    "Medium": {
        "advice": "You show moderate risk factors for asthma. Consider scheduling a pulmonary function test and managing known triggers like dust or allergens.",
        "disclaimer": "This system provides guidance, not a diagnosis. Please consult a healthcare professional."
    },
    "High": {
        "advice": "High risk detected. It is highly recommended to consult a pulmonologist immediately. You may need a rescue inhaler or controller medication.",
        "disclaimer": "Immediate consultation with a healthcare provider is suggested. Do not ignore severe symptoms."
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({"error": "Model not loaded on the server."}), 500
    
    data = request.json
    try:
        # Extract features
        age = int(data.get('age'))
        gender = int(data.get('gender')) # 0: Male, 1: Female, 2: Other
        bmi = float(data.get('bmi'))
        smoking = int(data.get('smoking_history'))
        family_history = int(data.get('family_history'))
        wheezing = int(data.get('wheezing'))
        sob = int(data.get('shortness_of_breath'))
        
        # Prepare features array (matching the training dataframe column order)
        # Order: age, gender, bmi, smoking, family_history, wheezing, shortness_of_breath
        input_data = [[
            age,
            gender,
            bmi,
            smoking,
            family_history,
            wheezing,
            sob
        ]]

        # Predict
        prediction = model.predict(input_data)[0]
        
        # Async-like log to supabase (but synchronous here)
        if supabase:
            try:
                db_data = {
                    "age": age,
                    "gender": "Male" if gender == 0 else ("Female" if gender == 1 else "Other"),
                    "bmi": bmi,
                    "smoking_history": bool(smoking),
                    "family_history": bool(family_history),
                    "wheezing": bool(wheezing),
                    "shortness_of_breath": bool(sob),
                    "predicted_risk": prediction
                }
                supabase.table("predictions_log").insert(db_data).execute()
            except Exception as db_e:
                print("Failed to save to Supabase:", db_e)

        return jsonify({
            "risk": prediction,
            "treatment": TREATMENTS[prediction]["advice"],
            "disclaimer": TREATMENTS[prediction]["disclaimer"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Provide WSGI application object for Vercel
# Vercel needs "app" exposed in index.py
if __name__ == '__main__':
    app.run(debug=True, port=5000)
