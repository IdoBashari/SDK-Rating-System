from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask_cors import CORS
import os

# Load environment variables
load_dotenv()

# Get MongoDB URI and JWT Secret
mongo_uri = os.getenv("MONGO_URI")
jwt_secret = os.getenv("JWT_SECRET_KEY")

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app)

# Configure app
app.config["MONGO_URI"] = mongo_uri
app.config["JWT_SECRET_KEY"] = jwt_secret
app.config["MONGO_CONNECT_TIMEOUT_MS"] = 5000

# Configure MongoDB
mongo = PyMongo(app)
app.mongo = mongo

# Import and register blueprints
from app.routes.user_routes import user_routes
from app.routes.rating_routes import rating_routes
from app.routes.comment_routes import comment_routes

app.register_blueprint(user_routes)
app.register_blueprint(rating_routes)
app.register_blueprint(comment_routes)

# Create indexes
with app.app_context():
    mongo.db.users.create_index("email", unique=True)
    mongo.db.ratings.create_index(
        [("user_id", 1), ("item_id", 1)],
        unique=True,
        name="unique_user_item_rating"
    )

# Root route
@app.route('/')
def index():
    return {"status": "ok"}