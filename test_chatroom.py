"""
Test ChatroomManager functionality
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.services.https.ChatroomManager import ChatroomManager
from app.services.https.UserManagement import UserManagement
from app.services.https.MatchManager import MatchManager
from app.core.database import Database


async def test_chatroom_manager():
    """Test basic ChatroomManager functionality"""
    print("=== Testing ChatroomManager ===")
    
    # Initialize database connection
    print("0. Connecting to database...")
    try:
        await Database.connect()
        print("   Database connected successfully")
    except Exception as e:
        print(f"   Database connection failed: {e}")
        print("   Continuing with in-memory testing only...")
    
    # Initialize managers
    user_manager = UserManagement()
    match_manager = MatchManager()
    chatroom_manager = ChatroomManager()
    
    # Test construction
    print("1. Testing ChatroomManager construction...")
    result = await chatroom_manager.construct()
    print(f"   Construction result: {result}")
    
    # Create test users if they don't exist
    print("2. Creating test users...")
    user_manager.create_new_user("test_user_1", 1001, 1)  # male
    user_manager.create_new_user("test_user_2", 1002, 2)  # female
    print("   Test users created")
    
    # Create a test match
    print("3. Creating test match...")
    match_id = match_manager.create_match(1001, 1002, "Test reason 1", "Test reason 2", 85).match_id
    print(f"   Created match ID: {match_id}")
    
    if match_id:
        # Test chatroom creation
        print("4. Testing chatroom creation...")
        chatroom_id = await chatroom_manager.get_or_create_chatroom(1001, 1002, match_id)
        print(f"   Created chatroom ID: {chatroom_id}")
        print(chatroom_id)
        
        if chatroom_id:
            # Test getting chat history (should be empty initially)
            print("5. Testing chat history retrieval...")
            history = chatroom_manager.get_chat_history(chatroom_id, 1001)
            print(f"   Chat history length: {len(history)}")
            
            # Test saving chatroom
            print("6. Testing chatroom save...")
            print(chatroom_id)
            save_result = await chatroom_manager.save_chatroom_history(chatroom_id)
            print(f"   Save result: {save_result}")
            
            # Test saving all chatrooms
            print("7. Testing save all chatrooms...")
            save_all_result = await chatroom_manager.save_chatroom_history()
            print(f"   Save all result: {save_all_result}")
            
            print("=== All tests completed ===")
            
            # Cleanup database connection
            try:
                await Database.close()
                print("   Database connection closed")
            except Exception as e:
                print(f"   Error closing database: {e}")
        else:
            print("   Failed to create chatroom")
    else:
        print("   Failed to create match")


if __name__ == "__main__":
    asyncio.run(test_chatroom_manager())