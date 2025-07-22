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

# Production server runs on port 4433
# Base URL: https://lovetapoversea.xyz:4433
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
- `app/WebSocketsService/` - WebSocket handlers (ConnectionHandler, MessageConnectionHandler, MatchSessionHandler)
- `app/ws/` - WebSocket routers (base, message, match)
- `app/core/` - Core components (database, security)
- `app/services/https/` - Business logic layer with singleton patterns
- `app/schemas/` - Pydantic models for request/response validation
- `app/objects/` - Data model classes (User, Match, Message, Chatroom)
- `app/utils/` - Utility modules (logging, singleton status)
- `logs/` - Application log files

### Key Architectural Patterns

**Layered Architecture**: Clear separation between API layer, service layer, and data layer.

**Singleton Services**: `UserManagement`, `MatchManager`, and `ChatroomManager` classes use singleton pattern for state management with in-memory storage and database persistence.

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
- `matches` - Match records between users
- `chatrooms` - Chatroom data with participant information
- `messages` - Message records with chatroom association

### Important: Database ID Handling and Performance Optimization
- **All entities use MongoDB `_id` field as primary key for O(log n) query performance**
- Users: `_id` stores user_id (telegram_id)
- Matches: `_id` stores match_id 
- Chatrooms: `_id` stores chatroom_id
- Messages: `_id` stores message_id
- All ObjectId fields are automatically converted to strings in responses
- Database-driven counter initialization prevents ID conflicts on server restart
- Query operations use `_id` field for optimal indexing performance

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
- `https://cupid-yukio-frontend-test.vercel.app` (test environment)
- `http://localhost:5173` (local development)
- `http://127.0.0.1:5173` (local IP)

**Note**: Server currently allows all origins (`allow_origins=["*"]`) in middleware configuration.

## API Endpoints

All endpoints are prefixed with `/api/v1/`:

### User Management (`/api/v1/UserManagement/`)
- `POST /create_new_user` - Create new user
- `POST /edit_user_age` - Update user age  
- `POST /edit_target_gender` - Update target gender preference
- `POST /edit_summary` - Update user bio/summary
- `POST /save_to_database` - Persist user data to MongoDB
- `POST /get_user_info_with_user_id` - Retrieve user information

### Match Management (`/api/v1/MatchManager/`)
- `POST /create_match` - Create new match between users
- `POST /get_match_info` - Get match information for user
- `POST /toggle_like` - Toggle like status for match
- `POST /save_to_database` - Save match to database

### Chatroom Management (`/api/v1/ChatroomManager/`)
- `POST /get_or_create_chatroom` - Get or create chatroom for users
- `POST /get_chat_history` - Retrieve chat history
- `POST /save_chatroom_history` - Save chatroom data to database

## WebSocket Endpoints

The application provides three WebSocket endpoints:

### Base WebSocket (`/ws/base`)
- General-purpose WebSocket with authentication and broadcast capabilities
- Uses `ConnectionHandler` for basic message handling

### Message WebSocket (`/ws/message`)
- Specialized for private messaging functionality
- Uses `MessageConnectionHandler` for private chat initialization and message routing
- Supports private chat init, private messages, and broadcast messages

### Match WebSocket (`/ws/match`)
- Specialized for match-making functionality
- Uses `MatchSessionHandler` for automatic match generation via N8n webhook integration
- Automatically creates matches and saves to database upon connection

## Business Logic Notes

### User Management Service
- In-memory user storage with MongoDB persistence using `_id` primary key
- Gender-based user categorization (male/female lists)
- Telegram ID integration for user identification
- Question parsing from telegram session `final_string` field
- Database-driven initialization from existing user records

### Match Management Service
- Singleton pattern with O(log n) database queries using `_id` indexing
- Database-driven counter initialization prevents match ID conflicts
- Comprehensive match loading from database on service startup
- Integration with UserManagement for bidirectional match tracking
- Match scoring and like status management
- **N8n Webhook Integration**: Automatic match generation via external webhook service
- **Duplicate Prevention**: Checks for existing matches between users to ensure uniqueness
- **Real-time Match Creation**: WebSocket-triggered match creation with immediate database persistence

### Chatroom Management Service  
- Database-driven counter initialization for both chatrooms and messages
- O(log n) query performance using `_id` primary key structure
- Automatic message and chatroom data loading on service initialization
- Message insurance mechanism with chatroom validation
- **Auto-Save Integration**: 10-second interval automatic persistence of chatroom data
- **Message Routing**: Real-time message delivery via WebSocket with database fallback
- **History Management**: Comprehensive chat history retrieval and management

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
- Singleton status logged before and after each request

### N8n Webhook Integration
- **Automatic Match Generation**: `/ws/match` WebSocket automatically requests matches from N8n webhook service
- **Match Creation Flow**: Upon WebSocket authentication, system requests 1 match, creates Match object, and saves to database
- **Duplicate Prevention**: System checks for existing matches between users to ensure uniqueness
- **Data Persistence**: Matches and updated user data automatically saved to database

### Auto-Save Background Task
- **10-Second Interval**: Automatic background task saves all singleton service data every 10 seconds
- **Service Coverage**: UserManagement, MatchManager, and ChatroomManager data automatically persisted
- **Error Handling**: Individual service save failures logged but don't stop other saves
- **Graceful Shutdown**: Final save operation performed during application shutdown
- **Performance Monitoring**: Save operations timed and logged for performance tracking

### Singleton Status Reporting
- **Real-time Monitoring**: `SingletonStatusReporter` provides status summaries for all services
- **Request Logging**: Before/after singleton states logged for each HTTP request
- **Debugging Support**: Comprehensive status information available for troubleshooting

## Development Status

**Completed**: 
- User management API with MongoDB integration using `_id` primary keys
- Comprehensive logging system with unique request IDs and singleton status tracking
- JWT framework and CORS configuration (currently allows all origins)
- Message system with chatroom assignment and insurance mechanisms
- WebSocket-based real-time messaging with private chat support
- Chatroom management with automatic creation from matches
- Data integrity validation for message-chatroom relationships
- **Performance optimization**: All entities migrated to use MongoDB `_id` field for O(log n) query performance
- **Service initialization**: Database-driven counter initialization prevents ID conflicts on server restart
- **Match system**: Automated match generation via N8n webhook integration
- **Auto-save system**: 10-second interval automatic database persistence for all services
- **Production deployment**: Server configured for lovetapoversea.xyz:4433

**Active Development**: 
- Advanced matching algorithms and scoring refinements
- Enhanced WebSocket connection management
- Real-time notifications and presence detection

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
  "_id": Number,  // message_id as primary key
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
- WebSocket connection testing (base, message, match endpoints)

WebSocket test files available:
- `frontend_base_test.js` - General WebSocket testing
- `frontend_message_test.js` - Message functionality testing
- `frontend_match_test.js` - Match system testing
- `websocket_test_suite.html` - Comprehensive WebSocket test suite
- `private_chat_test.html` - Private chat functionality testing
- `match_session_test.html` - Match session testing

No formal test framework is configured - tests are run as simple Python scripts and HTML test pages.

## Production Configuration

### Server Details
- **Production URL**: `https://lovetapoversea.xyz:4433`
- **Development URL**: `http://localhost:8000`
- **Protocol**: HTTP/HTTPS for API, WebSocket/WSS for real-time communication

### Frontend Integration
Comprehensive frontend integration documentation available in `FRONTEND_INTEGRATION_GUIDE.md` including:
- Complete API endpoint specifications
- WebSocket connection patterns
- Database schema documentation
- Authentication flows
- Error handling guidelines
- Performance considerations
- Security best practices