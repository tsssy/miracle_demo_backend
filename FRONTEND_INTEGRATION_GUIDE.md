# Frontend Integration Guide

This document provides comprehensive information for frontend developers to integrate with the NewLoveLushUserService backend API.

## Server Configuration

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://lovetapoversea.xyz:4433`

### Ports
- **HTTP API**: Port `8000` (development), Port `4433` (production)
- **WebSocket**: Port `8000` (development), Port `4433` (production)

## CORS Configuration

The backend supports CORS for the following origins:
- `https://cupid-yukio-frontend.vercel.app` (production)
- `https://cupid-yukio-frontend-test.vercel.app` (test environment)
- `http://localhost:5173` (local development)
- `http://127.0.0.1:5173` (local IP)

All HTTP methods and headers are allowed.

## HTTP REST API Endpoints

All HTTP endpoints are prefixed with `/api/v1/`.

### Authentication
Currently, the API uses simple user ID-based authentication. JWT is configured but not actively used.

### User Management Endpoints

Base path: `/api/v1/UserManagement/`

#### 1. Create New User
- **Endpoint**: `POST /api/v1/UserManagement/create_new_user`
- **Description**: Creates a new user in the system
- **Request Body**:
```json
{
  "telegram_user_name": "string",
  "telegram_user_id": 123456789,
  "gender": 1
}
```
- **Gender Values**: `1` (male), `2` (female), `3` (other)
- **Response**:
```json
{
  "success": true,
  "user_id": 123456789
}
```

#### 2. Edit User Age
- **Endpoint**: `POST /api/v1/UserManagement/edit_user_age`
- **Request Body**:
```json
{
  "user_id": 123456789,
  "age": 25
}
```
- **Response**:
```json
{
  "success": true
}
```

#### 3. Edit Target Gender
- **Endpoint**: `POST /api/v1/UserManagement/edit_target_gender`
- **Request Body**:
```json
{
  "user_id": 123456789,
  "target_gender": 2
}
```

#### 4. Edit User Summary
- **Endpoint**: `POST /api/v1/UserManagement/edit_summary`
- **Request Body**:
```json
{
  "user_id": 123456789,
  "summary": "I love traveling and photography!"
}
```

#### 5. Save User to Database
- **Endpoint**: `POST /api/v1/UserManagement/save_to_database`
- **Request Body**:
```json
{
  "user_id": 123456789
}
```
- **Note**: If `user_id` is omitted, saves all users

#### 6. Get User Information
- **Endpoint**: `POST /api/v1/UserManagement/get_user_info_with_user_id`
- **Request Body**:
```json
{
  "user_id": 123456789
}
```
- **Response**:
```json
{
  "user_id": 123456789,
  "telegram_user_name": "john_doe",
  "telegram_id": 123456789,
  "gender": 1,
  "age": 25,
  "target_gender": 2,
  "user_personality_trait": "I love traveling!",
  "match_ids": [1001, 1002, 1003]
}
```

### Match Management Endpoints

Base path: `/api/v1/MatchManager/`

#### 1. Create Match
- **Endpoint**: `POST /api/v1/MatchManager/create_match`
- **Request Body**:
```json
{
  "user_id_1": 123456789,
  "user_id_2": 987654321,
  "reason_1": "Both love photography",
  "reason_2": "Shared interest in travel",
  "match_score": 85
}
```
- **Response**:
```json
{
  "match_id": 1001
}
```

#### 2. Get Match Information
- **Endpoint**: `POST /api/v1/MatchManager/get_match_info`
- **Request Body**:
```json
{
  "user_id": 123456789,
  "match_id": 1001
}
```

#### 3. Toggle Like Status
- **Endpoint**: `POST /api/v1/MatchManager/toggle_like`
- **Request Body**:
```json
{
  "match_id": 1001
}
```

#### 4. Save Match to Database
- **Endpoint**: `POST /api/v1/MatchManager/save_to_database`
- **Request Body**:
```json
{
  "match_id": 1001
}
```

### Chatroom Management Endpoints

Base path: `/api/v1/ChatroomManager/`

#### 1. Get or Create Chatroom
- **Endpoint**: `POST /api/v1/ChatroomManager/get_or_create_chatroom`
- **Request Body**:
```json
{
  "user_id_1": 123456789,
  "user_id_2": 987654321,
  "match_id": 1001
}
```
- **Response**:
```json
{
  "success": true,
  "chatroom_id": 2001
}
```

#### 2. Get Chat History
- **Endpoint**: `POST /api/v1/ChatroomManager/get_chat_history`
- **Request Body**:
```json
{
  "chatroom_id": 2001,
  "user_id": 123456789
}
```
- **Response**:
```json
{
  "success": true,
  "messages": [
    {
      "sender_name": "john_doe",
      "message": "Hello there!",
      "datetime": "2023-12-01T10:30:00Z"
    }
  ]
}
```

#### 3. Save Chatroom History
- **Endpoint**: `POST /api/v1/ChatroomManager/save_chatroom_history`
- **Request Body**:
```json
{
  "chatroom_id": 2001
}
```

## WebSocket Connections

The backend provides three WebSocket endpoints for real-time communication:

### Base WebSocket: `/ws/base`

General-purpose WebSocket connection with authentication and broadcast capabilities.

**Connection Example**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/base');

ws.onopen = function() {
    // Send authentication message (REQUIRED)
    ws.send(JSON.stringify({
        user_id: "123456789"
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

**Authentication Response**:
```json
{
  "status": "authenticated",
  "user_id": "123456789"
}
```

### Message WebSocket: `/ws/message`

Specialized for messaging functionality including private chats.

**Connection Example**:
```javascript
const messageWs = new WebSocket('ws://localhost:8000/ws/message');

messageWs.onopen = function() {
    // Authentication required
    messageWs.send(JSON.stringify({
        user_id: "123456789"
    }));
};
```

**Message Types**:

#### 1. Private Chat Initialization
```javascript
messageWs.send(JSON.stringify({
    type: "private_chat_init",
    target_user_id: "987654321",
    match_id: 1001
}));
```

**Response Flow**:
```json
{
  "type": "private_chat_progress",
  "step": 1,
  "message": "正在获取或创建聊天室... (match_id: 1001)"
}
```

```json
{
  "type": "private_chat_progress",
  "step": 1,
  "status": "completed",
  "chatroom_id": 2001,
  "message": "聊天室已准备就绪 (chatroom_id: 2001)"
}
```

#### 2. Private Message
```javascript
messageWs.send(JSON.stringify({
    type: "private",
    target_user_id: "987654321",
    chatroom_id: 2001,
    content: "Hello there!",
    timestamp: new Date().toISOString()
}));
```

#### 3. Broadcast Message
```javascript
messageWs.send(JSON.stringify({
    type: "broadcast",
    content: "Hello everyone!",
    timestamp: new Date().toISOString()
}));
```

### Match WebSocket: `/ws/match`

Specialized for match-making functionality.

**Connection Example**:
```javascript
const matchWs = new WebSocket('ws://localhost:8000/ws/match');

matchWs.onopen = function() {
    // Authentication required
    matchWs.send(JSON.stringify({
        user_id: "123456789"
    }));
};
```

**Automatic Match Process**:
Upon successful authentication, the match system automatically:
1. Requests matches from N8n webhook service
2. Creates match records in the database
3. Sends match information to the client

**Match Information Response**:
```json
{
  "type": "match_info",
  "match_id": 1001,
  "self_user_id": 123456789,
  "matched_user_id": 987654321,
  "match_score": 85,
  "reason_of_match_given_to_self_user": "Both love photography",
  "reason_of_match_given_to_matched_user": "Shared interest in travel"
}
```

**Error Handling**:
```json
{
  "type": "match_error",
  "message": "No matches found"
}
```

## Error Handling

### HTTP Errors
- **400 Bad Request**: Invalid request parameters or validation errors
- **404 Not Found**: Resource not found (matches, users, chatrooms)
- **500 Internal Server Error**: Server-side errors

### WebSocket Errors
```json
{
  "error": "Authentication failed"
}
```

```json
{
  "error": "Invalid JSON format"
}
```

```json
{
  "type": "private_chat_error",
  "error": "target_user_id and match_id are required"
}
```

## Data Types and Validation

### Gender Values
- `1`: Male
- `2`: Female  
- `3`: Other

### User ID Format
- All user IDs are integers (Telegram IDs)
- WebSocket authentication accepts both string and integer formats
- Internal processing converts to appropriate types

### Date/Time Format
- ISO 8601 format: `"2023-12-01T10:30:00Z"`
- UTC timezone recommended

## Best Practices

### 1. WebSocket Connection Management
```javascript
class WebSocketManager {
    constructor(endpoint, userId) {
        this.endpoint = endpoint;
        this.userId = userId;
        this.ws = null;
        this.isAuthenticated = false;
    }
    
    connect() {
        this.ws = new WebSocket(this.endpoint);
        
        this.ws.onopen = () => {
            // Always send authentication first
            this.authenticate();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            // Implement reconnection logic
            this.reconnect();
        };
    }
    
    authenticate() {
        this.ws.send(JSON.stringify({
            user_id: this.userId
        }));
    }
    
    handleMessage(data) {
        if (data.status === 'authenticated') {
            this.isAuthenticated = true;
            this.onAuthenticated();
        }
        // Handle other message types...
    }
}
```

### 2. Error Handling
```javascript
async function makeAPICall(endpoint, data) {
    try {
        const response = await fetch(`http://localhost:8000/api/v1${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'API call failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
```

### 3. Message Queue for Offline Users
```javascript
class MessageQueue {
    constructor() {
        this.queue = [];
        this.isProcessing = false;
    }
    
    add(message) {
        this.queue.push(message);
        this.process();
    }
    
    async process() {
        if (this.isProcessing || this.queue.length === 0) return;
        
        this.isProcessing = true;
        while (this.queue.length > 0) {
            const message = this.queue.shift();
            try {
                await this.sendMessage(message);
            } catch (error) {
                // Re-queue on failure
                this.queue.unshift(message);
                break;
            }
        }
        this.isProcessing = false;
    }
}
```

## Development Environment Setup

### 1. Local Development
```bash
# Start backend server
python app/server_run.py

# Server will be available at:
# HTTP API: http://localhost:8000
# WebSocket: ws://localhost:8000
```

### 2. Frontend Configuration
```javascript
const config = {
    development: {
        apiUrl: 'http://localhost:8000/api/v1',
        wsUrl: 'ws://localhost:8000/ws'
    },
    production: {
        apiUrl: 'https://lovetapoversea.xyz:4433/api/v1',
        wsUrl: 'wss://lovetapoversea.xyz:4433/ws'
    }
};
```

### 3. Testing
Use the provided test files as references:
- `frontend_base_test.js` - General WebSocket testing
- `frontend_message_test.js` - Message functionality testing  
- `frontend_match_test.js` - Match system testing

## Database Schema Overview

The backend uses MongoDB with the following collections:

### Users Collection
```javascript
{
  "_id": 123456789,  // telegram_user_id (used as primary key)
  "telegram_user_name": "john_doe",
  "gender": 1,
  "age": 25,
  "target_gender": 2,
  "user_personality_summary": "I love traveling!",
  "match_ids": [1001, 1002]
}
```

### Matches Collection
```javascript
{
  "_id": 1001,  // match_id (used as primary key)
  "user_id_1": 123456789,
  "user_id_2": 987654321,
  "match_score": 85,
  "description_to_user_1": "Both love photography",
  "description_to_user_2": "Shared interest in travel",
  "is_liked": false,
  "mutual_game_scores": {},
  "chatroom_id": null,
  "created_at": 1701423000
}
```

### Chatrooms Collection
```javascript
{
  "_id": 2001,  // chatroom_id (used as primary key)
  "user1_id": 123456789,
  "user2_id": 987654321,
  "message_ids": [3001, 3002, 3003]
}
```

### Messages Collection
```javascript
{
  "_id": 3001,  // message_id (used as primary key)
  "message_content": "Hello there!",
  "message_send_time_in_utc": "2023-12-01T10:35:00.000Z",
  "message_sender_id": 123456789,
  "message_receiver_id": 987654321,
  "chatroom_id": 2001
}
```

## Performance Considerations

### 1. Database Optimization
- All entities use MongoDB `_id` field as primary key for O(log n) performance
- Automatic ObjectId to string conversion in responses
- Database-driven counter initialization prevents ID conflicts

### 2. Memory Management
- Services use singleton patterns with in-memory caching
- Automatic database persistence every 10 seconds
- Manual save endpoints available for immediate persistence

### 3. WebSocket Management
- Connection pooling with automatic cleanup
- Broadcast optimization with disconnection detection
- Message queueing for offline users

## Security Notes

### 1. Authentication
- Currently uses simple user ID verification
- JWT framework is implemented but not actively used
- User must exist in database for WebSocket authentication

### 2. Data Validation
- Pydantic models provide comprehensive input validation
- Gender values restricted to 1, 2, 3
- Required fields enforced at API level

### 3. Message Insurance
- Each message must belong to exactly one chatroom
- Real-time validation prevents cross-chatroom message leakage
- Database consistency validation available

## Troubleshooting

### Common Issues

#### 1. WebSocket Authentication Fails
```javascript
// Ensure user exists in database first
await fetch('http://localhost:8000/api/v1/UserManagement/get_user_info_with_user_id', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 123456789 })
});
```

#### 2. CORS Issues
- Verify your frontend URL is in the CORS whitelist
- For local development, use `http://localhost:5173` or `http://127.0.0.1:5173`

#### 3. Message Not Delivered
- Check if target user is connected via WebSocket
- Verify chatroom exists and users are participants
- Use message insurance validation methods

#### 4. Match Creation Fails
- Ensure both users exist in the system
- Check for duplicate matches (system prevents duplicates)
- Verify N8n webhook service is responding

### Debug Logging
The backend provides comprehensive logging:
- All HTTP requests/responses logged with unique IDs
- WebSocket connections and message flows tracked
- Database operations and errors logged
- Singleton service status reporting available

Check log files in the `logs/` directory for detailed debugging information.