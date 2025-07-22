import asyncio
from app.services.https.N8nWebhookManager import N8nWebhookManager


async def test_n8n_webhook_async():
    """Test the N8nWebhookManager async functionality"""
    webhook_manager = N8nWebhookManager()
    
    print("Testing N8n Webhook Manager (Async)")
    print("=" * 40)
    print(f"Testing connection to: {webhook_manager.base_url}")
    
    try:
        # Test with default num_of_matches (1)
        print("Test 1: Getting 1 match for user 1000000")
        matches = await webhook_manager.request_matches(1000000)
        print(f"✅ SUCCESS: Received {len(matches)} matches")
        for i, match in enumerate(matches, 1):
            print(f"  Match {i}:")
            print(f"    Self User ID: {match.get('self_user_id')}")
            print(f"    Matched User ID: {match.get('matched_user_id')}")
            print(f"    Match Score: {match.get('match_score')}")
            print(f"    Reason for Self: {match.get('reason_of_match_given_to_self_user')[:100]}...")
            print(f"    Reason for Matched: {match.get('reason_of_match_given_to_matched_user')[:100]}...")
            print()
        
        # Test with custom num_of_matches (3)
        print("Test 2: Getting 3 matches for user 1000000")
        matches = await webhook_manager.request_matches(1000000, 3)
        print(f"✅ SUCCESS: Received {len(matches)} matches")
        for i, match in enumerate(matches, 1):
            print(f"  Match {i}: User {match.get('matched_user_id')} (Score: {match.get('match_score')})")
        
    except Exception as e:
        print(f"❌ ERROR during async test: {e}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            print(f"HTTP Status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
    
    return True


def test_n8n_webhook_sync():
    """Test the N8nWebhookManager sync functionality"""
    webhook_manager = N8nWebhookManager()
    
    print("\nTesting N8n Webhook Manager (Sync)")
    print("=" * 40)
    
    try:
        # Test with default num_of_matches (1)
        print("Test 1: Getting 1 match for user 1000000")
        matches = webhook_manager.sync_request_matches(1000000)
        print(f"Received {len(matches)} matches:")
        for i, match in enumerate(matches, 1):
            print(f"  Match {i}:")
            print(f"    Self User ID: {match.get('self_user_id')}")
            print(f"    Matched User ID: {match.get('matched_user_id')}")
            print(f"    Match Score: {match.get('match_score')}")
            print(f"    Reason for Self: {match.get('reason_of_match_given_to_self_user')}")
            print(f"    Reason for Matched: {match.get('reason_of_match_given_to_matched_user')}")
            print()
        
        # Test with custom num_of_matches (3)
        print("Test 2: Getting 3 matches for user 1000000")
        matches = webhook_manager.sync_request_matches(1000000, 3)
        print(f"Received {len(matches)} matches:")
        for i, match in enumerate(matches, 1):
            print(f"  Match {i}: User {match.get('matched_user_id')} (Score: {match.get('match_score')})")
            
    except Exception as e:
        print(f"Error during sync test: {e}")


if __name__ == "__main__":
    # Run async test
    asyncio.run(test_n8n_webhook_async())
    
    # Run sync test
    test_n8n_webhook_sync()