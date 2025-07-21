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
- `chatrooms` - Chat room data with user pairs and message references
- `messages` - Individual messages with chatroom assignment
- `matches` - User matching data with optional chatroom references

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

### Message System & Chatroom Management
- **Message Insurance Mechanism**: Each message is assigned to exactly one chatroom via `chatroom_id`
- **Real-time Validation**: Message creation validates sender/receiver belong to specified chatroom
- **Data Integrity**: `Message.validate_message_chatroom_consistency()` checks database consistency
- **Chatroom Lifecycle**: Chatrooms are created when matches are established between users
- **Message Storage**: Messages stored in `messages` collection with chatroom assignment
- **Offline Message Support**: Messages persist for retrieval when users reconnect

### WebSocket Message Handling
- **Private Chat Initialization**: Two-step process (chatroom creation + history retrieval)
- **Message Types**: Support for private messages, broadcasts, and chat initialization
- **Real-time Delivery**: WebSocket-based message delivery with fallback to database storage
- **Connection Management**: User connection tracking for message routing

### Request/Response Logging
- Every request gets a unique ID (`req_[timestamp]`)
- Full request/response bodies are logged for debugging
- JSON parsing and pretty-printing in logs
- Processing time tracking

## Development Status

**Completed**: 
- User management API with MongoDB integration
- Comprehensive logging system with unique request IDs
- JWT framework and CORS configuration
- Message system with chatroom assignment and insurance mechanisms
- WebSocket-based real-time messaging with private chat support
- Chatroom management with automatic creation from matches
- Data integrity validation for message-chatroom relationships

**Active Development**: 
- Matching system (`MatchManager` class) - partially implemented
- User matching algorithms and scoring
- Match-based chatroom initialization

**Skeleton/Placeholder**: 
- Advanced matching features and algorithms
- Group chat functionality
- Message encryption and security features

## Message Insurance Mechanism

### Overview
A comprehensive data integrity system ensuring messages can only belong to one specific chatroom, preventing data corruption and cross-chatroom message leakage.

### Core Components

#### 1. Message-Chatroom Binding
```python
# Message constructor now requires chatroom_id
message = Message(sender_user, receiver_user, content, chatroom_id)
```

#### 2. Real-time Validation
- **Creation-time Checks**: `_validate_chatroom_membership()` validates during message creation
- **Chatroom Existence**: Verifies the specified chatroom exists in ChatroomManager
- **User Membership**: Ensures both sender and receiver belong to the specified chatroom
- **Immediate Failure**: Throws `ValueError` if validation fails, preventing invalid message creation

#### 3. Database Schema
```javascript
// messages collection schema
{
  "message_id": Number,
  "message_content": String,
  "message_send_time_in_utc": Date,
  "message_sender_id": Number,
  "message_receiver_id": Number,
  "chatroom_id": Number  // Insurance mechanism field
}
```

#### 4. Consistency Validation
```python
# Static method for database-wide consistency check
is_valid = await Message.validate_message_chatroom_consistency()
```

### Safety Features

- **Prevention**: Blocks invalid messages at creation time
- **Detection**: Database-wide consistency validation available
- **Migration**: Existing messages automatically assigned correct chatroom_id
- **Logging**: Detailed validation logging for debugging

### Usage Guidelines

1. **Always specify chatroom_id** when creating messages
2. **Use ChatroomManager.send_message()** for standard message sending (handles validation automatically)
3. **Run periodic consistency checks** in production environments
4. **Monitor logs** for validation failures indicating potential bugs

## Testing Approach

Basic API testing using `httpx` library. Tests focus on:
- User creation (male/female)
- Data retrieval by telegram_id
- Response format validation

No formal test framework is configured - tests are run as simple Python scripts.