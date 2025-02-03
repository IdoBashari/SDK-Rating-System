from flask import Blueprint, request, jsonify, current_app
from app.models.comment import Comment
from bson import ObjectId
import jwt
from datetime import datetime

comment_routes = Blueprint('comment_routes', __name__)

@comment_routes.route('/api/comments', methods=['POST'])
def create_comment():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['user_id', 'item_id', 'content']):
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
        
        # Create new comment object
        new_comment = Comment(
            user_id=str(user_id),
            item_id=data['item_id'],
            content=data['content']
        )
        
        # Validate comment data
        is_valid, error_message = new_comment.validate()
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Insert comment
        result = mongo.db.comments.insert_one(new_comment.to_dict())
        
        return jsonify({
            "message": "Comment created successfully",
            "comment_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comment_routes.route('/api/comments', methods=['GET'])
def get_comments():
    try:
        mongo = current_app.mongo
        
        # Get filters from query params
        user_id = request.args.get('user_id')
        item_id = request.args.get('item_id')
        
        # Build query based on filters
        query = {}
        if user_id:
            try:
                query['user_id'] = ObjectId(user_id)
            except:
                return jsonify({"error": "Invalid user_id format"}), 400
        if item_id:
            query['item_id'] = item_id
            
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        skip = (page - 1) * per_page
        
        # Get total count
        total_comments = mongo.db.comments.count_documents(query)
        
        # Get comments with pagination
        comments = list(mongo.db.comments.find(query).skip(skip).limit(per_page))
        
        # Process comments for response
        for comment in comments:
            comment['_id'] = str(comment['_id'])
            comment['user_id'] = str(comment['user_id'])
        
        return jsonify({
            "comments": comments,
            "page": page,
            "per_page": per_page,
            "total": total_comments,
            "total_pages": (total_comments + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comment_routes.route('/api/comments/<comment_id>', methods=['GET'])
def get_comment(comment_id):
    try:
        mongo = current_app.mongo
        object_id = ObjectId(comment_id)
        comment_data = mongo.db.comments.find_one({"_id": object_id})
        
        if not comment_data:
            return jsonify({"error": "Comment not found"}), 404
            
        # Convert ObjectId to string for JSON response
        comment_data['_id'] = str(comment_data['_id'])
        comment_data['user_id'] = str(comment_data['user_id'])
        
        return jsonify(comment_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comment_routes.route('/api/comments/<comment_id>', methods=['PUT'])
def update_comment(comment_id):
    try:
        mongo = current_app.mongo
        data = request.get_json()
        
        # Check if comment exists
        object_id = ObjectId(comment_id)
        existing_comment = mongo.db.comments.find_one({"_id": object_id})
        if not existing_comment:
            return jsonify({"error": "Comment not found"}), 404
            
        if 'content' not in data:
            return jsonify({"error": "Content is required for update"}), 400
            
        # Create Comment object for validation
        updated_comment = Comment(
            user_id=str(existing_comment['user_id']),
            item_id=existing_comment['item_id'],
            content=data['content']
        )
        
        # Validate updated data
        is_valid, error_message = updated_comment.validate()
        if not is_valid:
            return jsonify({"error": error_message}), 400
            
        # Perform update
        result = mongo.db.comments.update_one(
            {"_id": object_id},
            {"$set": {"content": data['content']}}
        )
        
        if result.modified_count > 0:
            # Get updated comment data
            updated_data = mongo.db.comments.find_one({"_id": object_id})
            updated_data['_id'] = str(updated_data['_id'])
            updated_data['user_id'] = str(updated_data['user_id'])
            return jsonify({
                "message": "Comment updated successfully",
                "comment": updated_data
            }), 200
        else:
            return jsonify({"message": "No changes made"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comment_routes.route('/api/comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    try:
        mongo = current_app.mongo
        object_id = ObjectId(comment_id)
        
        # Check if comment exists
        existing_comment = mongo.db.comments.find_one({"_id": object_id})
        if not existing_comment:
            return jsonify({"error": "Comment not found"}), 404
            
        # Delete comment
        result = mongo.db.comments.delete_one({"_id": object_id})
        
        if result.deleted_count > 0:
            return jsonify({
                "message": "Comment deleted successfully",
                "comment_id": comment_id
            }), 200
        else:
            return jsonify({"error": "Failed to delete comment"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500