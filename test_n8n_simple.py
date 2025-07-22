import asyncio
import httpx
import json
from typing import List, Dict


class SimpleN8nWebhookTester:
    def __init__(self):
        self.base_url = "http://8.216.32.239:5678/webhook/match"
        
    async def request_matches(self, user_id: int, num_of_matches: int = 1) -> List[Dict]:
        """
        Request matches from n8n webhook workflow
        """
        try:
            params = {
                "user_id": user_id,
                "num_of_matches": num_of_matches
            }
            
            print(f"Requesting matches for user_id={user_id}, num_of_matches={num_of_matches}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                matches = data.get("output", [])
                
                print(f"Received {len(matches)} matches for user {user_id}")
                return matches
                
        except httpx.HTTPError as e:
            print(f"HTTP error while requesting matches: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error in request_matches: {e}")
            raise
    
    def sync_request_matches(self, user_id: int, num_of_matches: int = 1) -> List[Dict]:
        """
        Synchronous version of request_matches
        """
        try:
            params = {
                "user_id": user_id,
                "num_of_matches": num_of_matches
            }
            
            print(f"Requesting matches (sync) for user_id={user_id}, num_of_matches={num_of_matches}")
            
            with httpx.Client() as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                matches = data.get("output", [])
                
                print(f"Received {len(matches)} matches for user {user_id}")
                return matches
                
        except httpx.HTTPError as e:
            print(f"HTTP error while requesting matches: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error in sync_request_matches: {e}")
            raise


async def test_n8n_webhook_async():
    """Test the N8n webhook functionality asynchronously"""
    webhook_tester = SimpleN8nWebhookTester()
    
    print("Testing N8n Webhook (Async)")
    print("=" * 40)
    
    try:
        # Test with default num_of_matches (1)
        print("Test 1: Getting 1 match for user 1000000")
        matches = await webhook_tester.request_matches(1000000)
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
        matches = await webhook_tester.request_matches(1000000, 3)
        print(f"Received {len(matches)} matches:")
        for i, match in enumerate(matches, 1):
            print(f"  Match {i}: User {match.get('matched_user_id')} (Score: {match.get('match_score')})")
        
    except Exception as e:
        print(f"Error during async test: {e}")


def test_n8n_webhook_sync():
    """Test the N8n webhook functionality synchronously"""
    webhook_tester = SimpleN8nWebhookTester()
    
    print("\nTesting N8n Webhook (Sync)")
    print("=" * 40)
    
    try:
        # Test with default num_of_matches (1)
        print("Test 1: Getting 1 match for user 1000000")
        matches = webhook_tester.sync_request_matches(1000000)
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
        matches = webhook_tester.sync_request_matches(1000000, 3)
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