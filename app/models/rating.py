from datetime import datetime
from bson import ObjectId

class Rating:
    def __init__(self, user_id, item_id, rating, description=None):
        self._id = ObjectId()
        self.user_id = ObjectId(user_id)  # Convert string ID to ObjectId
        self.item_id = str(item_id)       # Keep item_id as string
        self.rating = rating
        self.description = description
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert rating object to dictionary (for MongoDB)"""
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "item_id": self.item_id,
            "rating": self.rating,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create rating object from dictionary (from MongoDB)"""
        rating = Rating(
            user_id=str(data.get('user_id')),
            item_id=data.get('item_id'),
            rating=data.get('rating'),
            description=data.get('description')
        )
        rating._id = data.get('_id', ObjectId())
        rating.created_at = data.get('created_at', datetime.utcnow())
        return rating
    
    def validate(self):
        """Validate rating data"""
        if not isinstance(self.rating, (int, float)):
            return False, "Rating must be a number"
            
        if self.rating < 1 or self.rating > 5:
            return False, "Rating must be between 1 and 5"
            
        if self.description and len(self.description) > 500:
            return False, "Description must be less than 500 characters"
            
        return True, None