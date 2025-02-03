from flask import Blueprint, request, jsonify, current_app
from app.models.rating import Rating
from bson import ObjectId
import jwt
from datetime import datetime

rating_routes = Blueprint('rating_routes', __name__)

@rating_routes.route('/api/ratings', methods=['POST'])
def create_rating():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['user_id', 'item_id', 'rating']):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Convert user_id to ObjectId and validate format
        try:
            user_id = ObjectId(data['user_id'])
        except:
            return jsonify({"error": "Invalid user_id format"}), 400
            
        # Check if user exists
        mongo = current_app.mongo
        user = mongo.db.users.find_one({"_id": user_id})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Create new rating object
        new_rating = Rating(
            user_id=str(user_id),  # Pass as string to Rating class
            item_id=data['item_id'],
            rating=data['rating'],
            description=data.get('description')
        )
        
        # Validate rating data
        is_valid, error_message = new_rating.validate()
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Check if rating already exists for this user and item
        existing_rating = mongo.db.ratings.find_one({
            "user_id": user_id,
            "item_id": data['item_id']
        })
        if existing_rating:
            return jsonify({"error": "Rating already exists for this item"}), 409
        
        # Insert rating
        result = mongo.db.ratings.insert_one(new_rating.to_dict())
        
        return jsonify({
            "message": "Rating created successfully",
            "rating_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rating_routes.route('/api/ratings', methods=['GET'])
def get_ratings():
    try:
        mongo = current_app.mongo
        
        # Get filters from query params
        user_id = request.args.get('user_id')
        item_id = request.args.get('item_id')
        
        # Build query based on filters
        query = {}
        if user_id:
            try:
                query['user_id'] = ObjectId(user_id)  # המרה ל-ObjectId לצורך שאילתה
            except:
                return jsonify({"error": "Invalid user_id format"}), 400
        if item_id:
            query['item_id'] = item_id
            
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        skip = (page - 1) * per_page
        
        # Get total count
        total_ratings = mongo.db.ratings.count_documents(query)
        
        # Get ratings with pagination
        ratings = list(mongo.db.ratings.find(query).skip(skip).limit(per_page))
        
        # Process ratings for response - המרה חזרה לstrings
        for rating in ratings:
            rating['_id'] = str(rating['_id'])
            rating['user_id'] = str(rating['user_id'])
        
        return jsonify({
            "ratings": ratings,
            "page": page,
            "per_page": per_page,
            "total": total_ratings,
            "total_pages": (total_ratings + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Add these routes to rating_routes.py

@rating_routes.route('/api/ratings/<rating_id>', methods=['GET'])
def get_rating(rating_id):
    try:
        mongo = current_app.mongo
        object_id = ObjectId(rating_id)
        rating_data = mongo.db.ratings.find_one({"_id": object_id})
        
        if not rating_data:
            return jsonify({"error": "Rating not found"}), 404
            
        # Convert ObjectId to string for JSON response
        rating_data['_id'] = str(rating_data['_id'])
        rating_data['user_id'] = str(rating_data['user_id'])
        
        return jsonify(rating_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rating_routes.route('/api/ratings/<rating_id>', methods=['PUT'])
def update_rating(rating_id):
    try:
        mongo = current_app.mongo
        data = request.get_json()
        
        # Check if rating exists
        object_id = ObjectId(rating_id)
        existing_rating = mongo.db.ratings.find_one({"_id": object_id})
        if not existing_rating:
            return jsonify({"error": "Rating not found"}), 404
            
        # Create Rating object for validation
        updated_rating = Rating(
            user_id=str(existing_rating['user_id']),
            item_id=existing_rating['item_id'],
            rating=data.get('rating', existing_rating['rating']),
            description=data.get('description', existing_rating.get('description'))
        )
        
        # Validate updated data
        is_valid, error_message = updated_rating.validate()
        if not is_valid:
            return jsonify({"error": error_message}), 400
            
        # Create update document
        update_data = {}
        if 'rating' in data:
            update_data['rating'] = data['rating']
        if 'description' in data:
            update_data['description'] = data['description']
            
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
            
        # Perform update
        result = mongo.db.ratings.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Get updated rating data
            updated_data = mongo.db.ratings.find_one({"_id": object_id})
            updated_data['_id'] = str(updated_data['_id'])
            updated_data['user_id'] = str(updated_data['user_id'])
            return jsonify({
                "message": "Rating updated successfully",
                "rating": updated_data
            }), 200
        else:
            return jsonify({"message": "No changes made"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rating_routes.route('/api/ratings/<rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
    try:
        mongo = current_app.mongo
        object_id = ObjectId(rating_id)
        
        # Check if rating exists
        existing_rating = mongo.db.ratings.find_one({"_id": object_id})
        if not existing_rating:
            return jsonify({"error": "Rating not found"}), 404
            
        # Delete rating
        result = mongo.db.ratings.delete_one({"_id": object_id})
        
        if result.deleted_count > 0:
            return jsonify({
                "message": "Rating deleted successfully",
                "rating_id": rating_id
            }), 200
        else:
            return jsonify({"error": "Failed to delete rating"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500