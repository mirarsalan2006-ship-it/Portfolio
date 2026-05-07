import os
import firebase_admin
from firebase_admin import credentials, db # Import db if using Realtime Database, or firestore
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

# Check if running on a server (Render) or local
if os.environ.get('FIREBASE_CONFIG'):
    # Parse the JSON string from the environment variable
    service_account_info = json.loads(os.environ.get('FIREBASE_CONFIG'))
    cred = credentials.Certificate(service_account_info)
else:
    # Local development
    cred = credentials.Certificate('serviceAccountKey.json')

firebase_admin.initialize_app(cred)

def create_app():
    # Initialize the Flask application
    app = Flask(__name__)
    
    # Set a secret key for secure sessions
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-fallback-dev-key-here')

    # ---------------------------------------------------------
    # Firebase Initialization
    # ---------------------------------------------------------
    # We check if Firebase is already initialized to prevent errors 
    # during development reloading (Hot Reload).
    if not firebase_admin._apps:
        # Get the path to your Firebase Service Account JSON file from .env
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-key.json')
        
        try:
            cred = credentials.Certificate(cred_path)
            
            # If you are using Realtime Database (like in Theem Func Gen), include the databaseURL.
            # If using Firestore, you only need the creds.
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DB_URL') 
            })
            print("🟢 Firebase Admin SDK initialized successfully.")
        except Exception as e:
            print(f"🔴 Error initializing Firebase: {e}")

    # ---------------------------------------------------------
    # Blueprint Registration
    # ---------------------------------------------------------
    # Import routes here to avoid circular imports
    from app.main.routes import main_bp
    from app.projects.routes import projects_bp

    # Register the Blueprints with the Flask app
    app.register_blueprint(main_bp)
    
    # Prefixing the projects blueprint means all routes inside it start with /projects automatically
    app.register_blueprint(projects_bp, url_prefix='/projects')

    return app  