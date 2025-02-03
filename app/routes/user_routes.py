from flask import Blueprint, request, jsonify
from flask import current_app
from app.models.user import User
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/api/users/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['email', 'password']):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Validate email format
        if '@' not in data['email']:
            return jsonify({"error": "Invalid email format"}), 400
            
        # Validate password length
        if len(data['password']) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Create new user object
        new_user = User(
            email=data['email'],
            password=data['password'],
            name=data.get('name')
        )
        
        # Insert user using the mongo instance from app context
        mongo = current_app.mongo
        result = mongo.db.users.insert_one(new_user.to_dict())
        
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': str(result.inserted_id),
                'email': new_user.email,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": str(result.inserted_id),
                "email": new_user.email,
                "name": new_user.name
            }
        }), 201
        
    except DuplicateKeyError:
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_routes.route('/api/users/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['email', 'password']):
            return jsonify({"error": "Missing email or password"}), 400
        
        # Get user from database
        mongo = current_app.mongo
        user = mongo.db.users.find_one({"email": data['email']})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Check password
        if not check_password_hash(user['password'], data['password']):
            return jsonify({"error": "Invalid password"}), 401
            
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': str(user['_id']),
                'email': user['email'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user['_id']),
                "email": user['email'],
                "name": user.get('name')
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_routes.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        mongo = current_app.mongo
        object_id = ObjectId(user_id)
        user_data = mongo.db.users.find_one({"_id": object_id})
        
        if not user_data:
            return jsonify({"error": "User not found"}), 404
            
        user_data['_id'] = str(user_data['_id'])
        user_data.pop('password', None)
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_routes.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        mongo = current_app.mongo
        data = request.get_json()
        
        # Check if user exists
        object_id = ObjectId(user_id)
        existing_user = mongo.db.users.find_one({"_id": object_id})
        if not existing_user:
            return jsonify({"error": "User not found"}), 404
        
        # Create update document
        update_data = {}
        
        # Update only provided fields
        if 'name' in data:
            update_data['name'] = data['name']
        if 'email' in data:
            # Check if email already exists
            if data['email'] != existing_user['email']:
                email_exists = mongo.db.users.find_one({"email": data['email']})
                if email_exists:
                    return jsonify({"error": "Email already exists"}), 409
            update_data['email'] = data['email']
        if 'password' in data:
            # Validate new password length
            if len(data['password']) < 6:
                return jsonify({"error": "Password must be at least 6 characters"}), 400
            update_data['password'] = generate_password_hash(data['password'])
            
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
            
        # Perform update
        result = mongo.db.users.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Get updated user data
            updated_user = mongo.db.users.find_one({"_id": object_id})
            updated_user['_id'] = str(updated_user['_id'])
            updated_user.pop('password', None)
            return jsonify({
                "message": "User updated successfully",
                "user": updated_user
            }), 200
        else:
            return jsonify({"message": "No changes made"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_routes.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        mongo = current_app.mongo
        object_id = ObjectId(user_id)
        
        # Check if user exists
        existing_user = mongo.db.users.find_one({"_id": object_id})
        if not existing_user:
            return jsonify({"error": "User not found"}), 404
            
        # Delete user
        result = mongo.db.users.delete_one({"_id": object_id})
        
        if result.deleted_count > 0:
            return jsonify({
                "message": "User deleted successfully",
                "user_id": user_id
            }), 200
        else:
            return jsonify({"error": "Failed to delete user"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_routes.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        mongo = current_app.mongo
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Calculate skip value
        skip = (page - 1) * per_page
        
        # Get total count
        total_users = mongo.db.users.count_documents({})
        
        # Get users with pagination
        users = list(mongo.db.users.find().skip(skip).limit(per_page))
        
        # Process users for response
        for user in users:
            user['_id'] = str(user['_id'])
            user.pop('password', None)
            
        return jsonify({
            "users": users,
            "page": page,
            "per_page": per_page,
            "total": total_users,
            "total_pages": (total_users + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500