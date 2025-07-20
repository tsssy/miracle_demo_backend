# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based backend service for a social/dating application called "NewLoveLushUserService". The application is designed for user matching and management, with integration to Telegram for user authentication and data collection.

## Tech Stack

- **Framework**: FastAPI with Uvicorn server
- **Database**: MongoDB with Motor (async) and PyMongo (sync) drivers  
- **Authentication**: JWT tokens (configured but not actively used)
- **Validation**: Pydantic for request/response schemas
- **Environment**: python-dotenv for configuration

## Development Commands

### Server Management
```bash
# Start development server
python app/server_run.py

# Alternative using uvicorn directly
uvicorn app.server_run:app --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run basic API tests
python test_api.py

# Install dependencies
pip install -r requirements.txt
```

### Monitoring
```bash
# View application logs
tail -f logs/app.log
```

## Architecture

### Directory Structure
- `app/api/v1/` - API endpoints and route definitions
- `app/core/` - Core components (database, security)
- `app/services/` - Business logic layer with singleton patterns
- `app/schemas/` - Pydantic models for request/response validation
- `app/utils/` - Utility modules (logging, etc.)
- `logs/` - Application log files

### Key Architectural Patterns

**Layered Architecture**: Clear separation between API layer, service layer, and data layer.

**Singleton Services**: `UserManagement` and `MatchManager` classes use singleton pattern for state management with in-memory storage.

**Database Abstraction**: Custom `Database` class in `app/core/database.py` provides async MongoDB operations with automatic ObjectId to string conversion.

**Comprehensive Logging**: All requests/responses are automatically logged with unique request IDs for debugging.

## Database Configuration

### Required Environment Variables
```bash
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=lovelush_users
MONGODB_USERNAME=root
MONGODB_PASSWORD=your_password
MONGODB_AUTH_SOURCE=admin
```

### Expected Collections
- `users` - User profiles and data
- `telegram_sessions` - Telegram integration data  
- `Question` - User-generated questions

### Important: Database ID Handling
- Users have custom `_id` values (user_id as document ID)
- All ObjectId fields are automatically converted to strings in responses
- MongoDB operations should use ObjectId for querying existing records

## CORS Configuration

The application supports multiple CORS configuration modes:

### Environment-Based CORS
```bash
# Allow all origins (development)
CORS_ALLOW_ALL=true

# Specific origins (production)
CORS_EXTRA_ORIGINS=https://domain1.com,https://domain2.com
```

### Default Allowed Origins
- `https://cupid-yukio-frontend.vercel.app` (production)
- `http://localhost:5173` (local development)
- `http://127.0.0.1:5173` (local IP)

## API Endpoints

All endpoints are prefixed with `/api/v1/users/`:

- `POST /create_new_user` - Create new user
- `POST /edit_user_age` - Update user age  
- `POST /edit_target_gender` - Update target gender preference
- `POST /edit_summary` - Update user bio/summary
- `POST /save_to_database` - Persist user data to MongoDB
- `POST /get_user_info_with_user_id` - Retrieve user information

## Business Logic Notes

### User Management Service
- In-memory user storage with MongoDB persistence
- Gender-based user categorization (male/female lists)
- Telegram ID integration for user identification
- Question parsing from telegram session `final_string` field

### Request/Response Logging
- Every request gets a unique ID (`req_[timestamp]`)
- Full request/response bodies are logged for debugging
- JSON parsing and pretty-printing in logs
- Processing time tracking

## Development Status

**Completed**: User management API, MongoDB integration, comprehensive logging, JWT framework, CORS configuration

**Skeleton/Placeholder**: Matching system (`service_match.py`), chatroom functionality (`service_chatroom.py`), WebSocket handling (`service_connection_handler.py`)

## Testing Approach

Basic API testing using `httpx` library. Tests focus on:
- User creation (male/female)
- Data retrieval by telegram_id
- Response format validation

No formal test framework is configured - tests are run as simple Python scripts.