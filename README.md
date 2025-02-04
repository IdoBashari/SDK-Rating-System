# Flask MongoDB API

Backend server for the Library Management Application, providing authentication, ratings, and comments functionality. This server serves as a demonstration backend for implementing a review and rating system that can be integrated with any client application.

## Features

- User authentication with JWT
- CRUD operations for users, ratings, and comments
- MongoDB integration
- Pagination support
- Input validation
- CORS enabled
- Vercel deployment ready

## Prerequisites

- Python 3.x
- MongoDB
- pip

## Environment Variables

Create a `.env` file in the root directory with:

```env
MONGO_URI=your_mongodb_connection_string
JWT_SECRET_KEY=your_jwt_secret_key
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables
4. Run the application:
```bash
python main.py
```

## API Endpoints

### Users
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users` - Get all users (paginated)
- `GET /api/users/<user_id>` - Get specific user
- `PUT /api/users/<user_id>` - Update user
- `DELETE /api/users/<user_id>` - Delete user

### Ratings
- `POST /api/ratings` - Create new rating
- `GET /api/ratings` - Get all ratings (paginated)
- `GET /api/ratings/<rating_id>` - Get specific rating
- `PUT /api/ratings/<rating_id>` - Update rating
- `DELETE /api/ratings/<rating_id>` - Delete rating

### Comments
- `POST /api/comments` - Create new comment
- `GET /api/comments` - Get all comments (paginated)
- `GET /api/comments/<comment_id>` - Get specific comment
- `PUT /api/comments/<comment_id>` - Update comment
- `DELETE /api/comments/<comment_id>` - Delete comment

## Models

### User
```python
{
    "_id": ObjectId,
    "email": string,
    "password": string (hashed),
    "name": string (optional),
    "created_at": datetime
}
```

### Rating
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "item_id": string,
    "rating": number (1-5),
    "description": string (optional),
    "created_at": datetime
}
```

### Comment
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "item_id": string,
    "content": string,
    "created_at": datetime
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error

## Deployment

The project is configured for Vercel deployment with `vercel.json`. To deploy:

1. Install Vercel CLI
2. Run `vercel` in project directory
3. Configure environment variables in Vercel dashboard

## Security Features

- Password hashing using Werkzeug
- JWT authentication
- Input validation
- MongoDB injection prevention
- CORS protection

## Development

To run in development mode:

```bash
export FLASK_ENV=development
flask run
```

## License

MIT