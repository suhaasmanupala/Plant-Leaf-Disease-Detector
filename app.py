
from flask import Flask, render_template, request, session, redirect, url_for, flash
from PIL import Image
import torch
from torchvision import transforms, models
from remedies import remedies
import random
import logging
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key in production

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

MODEL_PATH = 'plant_disease_resnet18.pth'
CLASS_NAMES_PATH = 'class_names.txt'
DB_PATH = 'detections.db'

# Initialize SQLite database
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            prediction TEXT,
            severity TEXT,
            confidence REAL,
            remedy_organic TEXT,
            remedy_chemical TEXT,
            remedy_preventive TEXT,
            scientific_name TEXT,
            cause TEXT,
            chemical_compounds TEXT,
            image_url TEXT,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        conn.commit()

# Load class names
with open(CLASS_NAMES_PATH) as f:
    class_names = [line.strip() for line in f.readlines()]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model - architecture must match training (ResNet18)
model = models.resnet18(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()
model.to(device)

# Transform pipeline matching training val_transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

# Improved leaf detection heuristic
def is_leaf_image(image, species=None):
    # Temporary bypass for testing
    logging.debug(f"Species received: {species}")
    # Comment out the bypass and uncomment the heuristic for production
    # return True  # Bypass to test if predictions work
    try:
        pixels = image.convert('RGB').getdata()
        green_count = sum(1 for r, g, b in pixels if g > r and g > b and g > 50)  # Lowered g > 50
        total_pixels = len(pixels)
        green_ratio = green_count / total_pixels if total_pixels > 0 else 0
        logging.debug(f"Green pixel ratio: {green_ratio:.3f}, Species: {species}")
        # Accept if green ratio is above 0.05 or a valid species is selected
        valid_species = ['Tomato', 'Potato', 'Corn', 'Apple', 'Grape', '']
        return green_ratio > 0.05 or species in valid_species
    except Exception as e:
        logging.error(f"Error in is_leaf_image: {str(e)}")
        return False

# Mock severity and remedy splitting logic
def get_severity_and_remedies(prediction):
    if not prediction:
        return "unknown", "severity-unknown", "No organic remedy available.", "No chemical remedy available.", "No preventive measures available.", "Unknown", "Unknown", "None"

    # Simulated severity
    severity_map = {
        "Bacterial Spot": "moderate",
        "Early Blight": "severe",
        "healthy": "mild",
        "Leaf Mold": "moderate",
        "Mosaic virus": "severe",
        "Septoria Leaf Spot": "moderate",
        "Spider mites": "mild",
        "Yellow Leafcurl virus": "severe"
    }
    severity = severity_map.get(prediction, "moderate")
    severity_class = f"severity-{severity}"

    # Get remedies and scientific details
    remedy_info = remedies.get(prediction, {
        "base_remedy": "No specific remedy available.",
        "scientific_name": "Unknown",
        "cause": "Unknown",
        "chemical_compounds": "None"
    })
    base_remedy = remedy_info["base_remedy"]
    scientific_name = remedy_info["scientific_name"]
    cause = remedy_info["cause"]
    chemical_compounds = remedy_info["chemical_compounds"]

    if prediction == "healthy":
        remedy_organic = "Continue using organic compost and monitor soil health."
        remedy_chemical = "No chemical treatment needed."
        remedy_preventive = base_remedy
    else:
        remedy_organic = f"Apply neem oil or {base_remedy.lower()}"
        remedy_chemical = f"Use copper-based fungicide or {base_remedy.lower()}"
        remedy_preventive = f"Ensure proper spacing and {base_remedy.lower()}"

    logging.debug(f"Prediction: {prediction}, Remedies: {remedy_organic}, {remedy_chemical}, {remedy_preventive}")
    return severity, severity_class, remedy_organic, remedy_chemical, remedy_preventive, scientific_name, cause, chemical_compounds

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    remedy_organic = "No organic remedy available."
    remedy_chemical = "No chemical remedy available."
    remedy_preventive = "No preventive measures available."
    image_url = None
    confidence = None
    severity = None
    severity_class = None
    scientific_name = "Unknown"
    cause = "Unknown"
    chemical_compounds = "None"

    if request.method == 'POST':
        logging.debug(f"Form data: {request.form}")
        logging.debug(f"Files: {request.files}")
        if 'file' not in request.files:
            logging.error("No file part in request")
            flash("No file part in request", "error")
            return render_template('index.html', error='No file part',
                                 prediction=prediction, remedy_organic=remedy_organic,
                                 remedy_chemical=remedy_chemical, remedy_preventive=remedy_preventive,
                                 image_url=image_url, confidence=confidence,
                                 severity=severity, severity_class=severity_class,
                                 scientific_name=scientific_name, cause=cause, chemical_compounds=chemical_compounds)
        file = request.files['file']
        species = request.form.get('plant-species', '')
        logging.debug(f"Selected species: {species}")
        if file.filename == '':
            logging.error("No selected file")
            flash("No selected file", "error")
            return render_template('index.html', error='No selected file',
                                 prediction=prediction, remedy_organic=remedy_organic,
                                 remedy_chemical=remedy_chemical, remedy_preventive=remedy_preventive,
                                 image_url=image_url, confidence=confidence,
                                 severity=severity, severity_class=severity_class,
                                 scientific_name=scientific_name, cause=cause, chemical_compounds=chemical_compounds)
        if file:
            try:
                image = Image.open(file.stream).convert('RGB')
                # Check if image is a leaf
                if not is_leaf_image(image, species):
                    logging.error("Invalid image: not a leaf")
                    flash("Invalid image: not a leaf", "error")
                    return render_template('index.html', error='Invalid image: not a leaf',
                                         prediction=prediction, remedy_organic=remedy_organic,
                                         remedy_chemical=remedy_chemical, remedy_preventive=remedy_preventive,
                                         image_url=image_url, confidence=confidence,
                                         severity=severity, severity_class=severity_class,
                                         scientific_name=scientific_name, cause=cause, chemical_compounds=chemical_compounds)
                input_tensor = transform(image).unsqueeze(0).to(device)
                with torch.no_grad():
                    outputs = model(input_tensor)
                    probs = torch.softmax(outputs, dim=1)
                    confidence = torch.max(probs).item() * 100
                    _, pred = torch.max(outputs, 1)
                    prediction = class_names[pred.item()]
                    severity, severity_class, remedy_organic, remedy_chemical, remedy_preventive, scientific_name, cause, chemical_compounds = get_severity_and_remedies(prediction)

                # Save uploaded image for display
                save_path = f'static/uploaded_leaf_{int(datetime.now().timestamp())}.jpg'
                image.save(save_path)
                image_url = '/' + save_path
                flash("Image processed successfully!", "success")
            except Exception as e:
                logging.error(f"Error processing image: {str(e)}")
                flash(f"Error processing image: {str(e)}", "error")
                return render_template('index.html', error=f'Error processing image: {str(e)}',
                                     prediction=prediction, remedy_organic=remedy_organic,
                                     remedy_chemical=remedy_chemical, remedy_preventive=remedy_preventive,
                                     image_url=image_url, confidence=confidence,
                                     severity=severity, severity_class=severity_class,
                                     scientific_name=scientific_name, cause=cause, chemical_compounds=chemical_compounds)

    return render_template('index.html', 
                         prediction=prediction, 
                         remedy_organic=remedy_organic,
                         remedy_chemical=remedy_chemical,
                         remedy_preventive=remedy_preventive,
                         image_url=image_url,
                         confidence=round(confidence, 2) if confidence else None,
                         severity=severity,
                         severity_class=severity_class,
                         scientific_name=scientific_name,
                         cause=cause,
                         chemical_compounds=chemical_compounds)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()
            if user:
                session['username'] = username
                session['user_id'] = user[0]
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid username or password", "error")
                return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                session['username'] = username
                c.execute('SELECT id FROM users WHERE username = ?', (username,))
                session['user_id'] = c.fetchone()[0]
                flash('Registration successful! You are now logged in.', 'success')
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                flash('Username already exists', 'error')
                return render_template('register.html', error='Username already exists')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('index'))

@app.route('/save_detection', methods=['POST'])
def save_detection():
    if not session.get('username'):
        flash("Please log in to save detections", "error")
        return redirect(url_for('login'))
    
    try:
        logging.debug(f"Save detection form data: {request.form}")
        logging.debug(f"Session data: {session}")
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO detections (
                user_id, prediction, severity, confidence, remedy_organic, remedy_chemical, 
                remedy_preventive, scientific_name, cause, chemical_compounds, image_url, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                session['user_id'],
                request.form.get('prediction', ''),
                request.form.get('severity', ''),
                float(request.form.get('confidence', 0)),
                request.form.get('remedy_organic', ''),
                request.form.get('remedy_chemical', ''),
                request.form.get('remedy_preventive', ''),
                request.form.get('scientific_name', ''),
                request.form.get('cause', ''),
                request.form.get('chemical_compounds', ''),
                request.form.get('image_url', ''),
                datetime.now().isoformat()
            ))
            conn.commit()
            flash("Detection saved to My Garden!", "success")
    except Exception as e:
        logging.error(f"Error saving detection: {str(e)}")
        flash(f"Error saving detection: {str(e)}", "error")
    return redirect(url_for('index'))

@app.route('/garden')
def garden():
    if not session.get('username'):
        flash("Please log in to view My Garden", "error")
        return redirect(url_for('login'))
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT prediction, severity, confidence, remedy_organic, remedy_chemical, remedy_preventive, scientific_name, cause, chemical_compounds, image_url, timestamp FROM detections WHERE user_id = ?', (session['user_id'],))
            detections = c.fetchall()
            logging.debug(f"Fetched detections: {detections}")
    except Exception as e:
        logging.error(f"Error fetching detections: {str(e)}")
        flash(f"Error fetching detections: {str(e)}", "error")
        detections = []
    return render_template('garden.html', detections=detections, username=session.get('username'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
