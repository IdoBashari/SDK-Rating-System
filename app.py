from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask_cors import CORS
import os
import json
from datetime import datetime

def create_app():
    print("\n=== Starting Application Creation ===")
    
    # Load environment variables
    load_dotenv()
    print("✓ Environment variables loaded")
    
    # Get MongoDB URI and JWT Secret
    mongo_uri = os.getenv("MONGO_URI")
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    print(f"✓ MONGO_URI loaded: {mongo_uri[:20]}...")
    print("✓ JWT_SECRET_KEY loaded")
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Add CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    print("✓ CORS configured")

    @app.route('/')
    def home():
        return jsonify({
            "status": "running",
            "version": "1.0",
            "endpoints": "/api/*"
        }), 200

    # Add logging configuration
    @app.errorhandler(500)
    def handle_server_error(e):
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "path": request.path,
            "method": request.method,
            "time": datetime.utcnow().isoformat()
        }
        print("❌ Server Error:", json.dumps(error_details, indent=2))
        return jsonify({"error": "Internal Server Error", "details": error_details}), 500

    @app.before_request
    def log_request():
        print(f"📝 Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        print(f"📋 Response: {response.status}")
        return response
    
    # Configure app
    app.config["MONGO_URI"] = mongo_uri
    app.config["JWT_SECRET_KEY"] = jwt_secret
    app.config["MONGO_CONNECT_TIMEOUT_MS"] = 5000  # 5 seconds timeout
    print("✓ App configuration completed")
    
    # Configure MongoDB
    try:
        print("Starting MongoDB configuration...")
        
        print("Creating PyMongo instance...")
        mongo = PyMongo(app)
        print("✓ PyMongo instance created")
        
        print("Testing MongoDB connection...")
        db = mongo.db
        print(f"✓ MongoDB database object created: {type(db)}")
        
        _ = db.list_collection_names()
        print("✓ Successfully retrieved collections list")
        
        app.mongo = mongo
        print("✓ MongoDB instance attached to app")
        
    except Exception as e:
        print(f"\n✕ MongoDB Error Details:")
        print(f"Error Type: {type(e)}")
        print(f"Error Message: {str(e)}")
        print(f"✕ Failed during MongoDB setup")
        raise e

    # Import routes
    from app.routes.user_routes import user_routes
    from app.routes.rating_routes import rating_routes
    from app.routes.comment_routes import comment_routes
    print("✓ Routes imported")
    
    # Register blueprints
    app.register_blueprint(user_routes)
    app.register_blueprint(rating_routes)
    app.register_blueprint(comment_routes)
    print("✓ Blueprints registered")
    
    try:
        print("\nCreating database indexes...")
        # User indexes
        mongo.db.users.create_index("email", unique=True)
        
        # Rating indexes - compound index for unique user ratings per item
        mongo.db.ratings.create_index(
            [("user_id", 1), ("item_id", 1)],
            unique=True,
            name="unique_user_item_rating"
        )
        print("✓ MongoDB indexes created successfully")
    except Exception as e:
        print(f"✕ Error creating indexes: {e}")
    
    print("=== Application Creation Completed ===\n")
    return app

if __name__ == "__main__":
    try:
        print("\n=== Starting Server ===")
        app = create_app()
        print("✓ App created successfully")
        app.run(debug=False)  # Remove debug mode for production
    except Exception as e:
        print(f"✕ Failed to start server: {str(e)}")
        exit(1)