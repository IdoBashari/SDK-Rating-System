from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask_cors import CORS
import os
import jwt

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["MONGO_CONNECT_TIMEOUT_MS"] = 5000

# Configure CORS
CORS(app)

# Configure MongoDB
mongo = PyMongo(app)
app.mongo = mongo

# Import and register blueprints
from app.routes.user_routes import user_routes
from app.routes.rating_routes import rating_routes
from app.routes.comment_routes import comment_routes

app.register_blueprint(user_routes, url_prefix='/api')
app.register_blueprint(rating_routes, url_prefix='/api')
app.register_blueprint(comment_routes, url_prefix='/api')

@app.route('/')
def home():
   return {"message": "API is running"}

# Export for vercel
application = app