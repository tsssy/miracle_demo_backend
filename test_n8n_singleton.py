#!/usr/bin/env python3
"""
Test script to verify N8nWebhookManager singleton implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.https.N8nWebhookManager import N8nWebhookManager

def test_singleton_pattern():
    """Test that N8nWebhookManager follows singleton pattern"""
    print("Testing N8nWebhookManager singleton pattern...")
    
    # Create multiple instances
    instance1 = N8nWebhookManager()
    instance2 = N8nWebhookManager()
    instance3 = N8nWebhookManager()
    
    # Test that all instances are the same object
    print(f"Instance 1 ID: {id(instance1)}")
    print(f"Instance 2 ID: {id(instance2)}")
    print(f"Instance 3 ID: {id(instance3)}")
    
    # Verify they are the same instance
    assert instance1 is instance2, "instance1 and instance2 should be the same object"
    assert instance2 is instance3, "instance2 and instance3 should be the same object"
    assert instance1 is instance3, "instance1 and instance3 should be the same object"
    
    # Test that they have the same attributes
    print(f"Instance 1 base_url: {instance1.base_url}")
    print(f"Instance 2 base_url: {instance2.base_url}")
    print(f"Instance 3 base_url: {instance3.base_url}")
    
    assert instance1.base_url == instance2.base_url == instance3.base_url
    
    # Test modifying one affects all (since they're the same object)
    original_url = instance1.base_url
    test_url = "http://test-url.com"
    instance1.base_url = test_url
    
    assert instance2.base_url == test_url, "Modifying instance1 should affect instance2"
    assert instance3.base_url == test_url, "Modifying instance1 should affect instance3"
    
    # Restore original URL
    instance1.base_url = original_url
    
    print("✓ All singleton tests passed!")
    return True

def test_singleton_with_inheritance():
    """Test that singleton pattern works correctly with inheritance"""
    print("\nTesting singleton with class references...")
    
    # Test using class directly
    manager1 = N8nWebhookManager()
    manager2 = N8nWebhookManager()
    
    # Test that class variables are properly maintained
    print(f"Class _initialized: {N8nWebhookManager._initialized}")
    print(f"Class _instance is not None: {N8nWebhookManager._instance is not None}")
    
    # Verify singleton instance is stored in class variable
    assert N8nWebhookManager._instance is manager1
    assert N8nWebhookManager._instance is manager2
    
    print("✓ Inheritance and class variable tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_singleton_pattern()
        test_singleton_with_inheritance()
        print("\n🎉 All tests passed! N8nWebhookManager is properly implemented as a singleton.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)