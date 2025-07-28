import httpx
import json
from typing import List, Dict
from app.utils.my_logger import MyLogger

logger = MyLogger(__name__)


class N8nWebhookManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(N8nWebhookManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.base_url = "http://8.216.32.239:5678/webhook/match"
            N8nWebhookManager._initialized = True
        
    async def request_matches(self, user_id: int, num_of_matches: int = 1) -> List[Dict]:
        """
        Request matches from n8n webhook workflow
        
        Args:
            user_id (int): The user ID to get matches for
            num_of_matches (int): Number of matches to request (default: 1)
            
        Returns:
            List[Dict]: List of match dictionaries with match details
        """
        try:
            params = {
                "user_id": user_id,
                "num_of_matches": num_of_matches
            }
            
            logger.info(f"Requesting matches for user_id={user_id}, num_of_matches={num_of_matches}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                matches = data.get("output", [])
                
                # 🔧 MODIFIED: 添加详细的N8n响应日志以调试description问题
                logger.info(f"Received {len(matches)} matches for user {user_id}")
                if matches:
                    logger.info(f"First match data structure: {matches[0]}")
                
                return matches
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while requesting matches: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in request_matches: {e}")
            raise
    
    def sync_request_matches(self, user_id: int, num_of_matches: int = 1) -> List[Dict]:
        """
        Synchronous version of request_matches for non-async contexts
        
        Args:
            user_id (int): The user ID to get matches for
            num_of_matches (int): Number of matches to request (default: 1)
            
        Returns:
            List[Dict]: List of match dictionaries with match details
        """
        try:
            params = {
                "user_id": user_id,
                "num_of_matches": num_of_matches
            }
            
            logger.info(f"Requesting matches (sync) for user_id={user_id}, num_of_matches={num_of_matches}")
            
            with httpx.Client(timeout=60.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                matches = data.get("output", [])
                
                logger.info(f"Received {len(matches)} matches for user {user_id}")
                return matches
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while requesting matches: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in sync_request_matches: {e}")
            raise