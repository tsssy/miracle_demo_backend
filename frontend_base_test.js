// Test script for /ws/base WebSocket handler
console.log('Testing /ws/base WebSocket connection...');

const baseWs = new WebSocket('ws://localhost:8000/ws/base');

baseWs.onopen = function() {
    console.log('✅ Connected to /ws/base');
    
    // Send authentication message
    const authMessage = {
        user_id: "test_user_base"
    };
    console.log('🔐 Sending authentication:', authMessage);
    baseWs.send(JSON.stringify(authMessage));
};

baseWs.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('📨 Received from /ws/base:', data);
    
    if (data.status === 'authenticated') {
        console.log('✅ Authentication successful for user:', data.user_id);
        
        // Send a test message after authentication
        setTimeout(() => {
            const testMessage = {
                content: "Hello from base test client!",
                timestamp: new Date().toISOString()
            };
            console.log('📤 Sending test message:', testMessage);
            baseWs.send(JSON.stringify(testMessage));
        }, 1000);
    }
};

baseWs.onclose = function() {
    console.log('❌ /ws/base connection closed');
};

baseWs.onerror = function(error) {
    console.log('⚠️ /ws/base error:', error);
};