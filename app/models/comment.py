from datetime import datetime
from bson import ObjectId

class Comment:
    def __init__(self, user_id, item_id, content):
        self._id = ObjectId()
        self.user_id = ObjectId(user_id)  # Convert string ID to ObjectId
        self.item_id = str(item_id)       # Keep item_id as string
        self.content = content
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert comment object to dictionary (for MongoDB)"""
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "item_id": self.item_id,
            "content": self.content,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create comment object from dictionary (from MongoDB)"""
        comment = Comment(
            user_id=str(data.get('user_id')),
            item_id=data.get('item_id'),
            content=data.get('content')
        )
        comment._id = data.get('_id', ObjectId())
        comment.created_at = data.get('created_at', datetime.utcnow())
        return comment
    
    def validate(self):
        """Validate comment data"""
        if not self.content:
            return False, "Content cannot be empty"
            
        if len(self.content) > 1000:
            return False, "Content must be less than 1000 characters"
            
        return True, None