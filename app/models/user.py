from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, email, password, name=None):
        self._id = ObjectId()
        self.email = email
        self.password = generate_password_hash(password)
        self.name = name
        self.created_at = datetime.utcnow()
    
    def check_password(self, password):
        """Verify the password"""
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        """Convert user object to dictionary (for MongoDB)"""
        return {
            "_id": self._id,
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create user object from dictionary (from MongoDB)"""
        user = User(
            email=data.get('email'),
            password="temp",
            name=data.get('name')
        )
        user._id = data.get('_id', ObjectId())
        user.password = data.get('password')
        user.created_at = data.get('created_at', datetime.utcnow())
        return user