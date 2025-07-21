// Test script for /ws/message WebSocket handler
console.log('Testing /ws/message WebSocket connection...');

const messageWs = new WebSocket('ws://localhost:8000/ws/message');

messageWs.onopen = function() {
    console.log('✅ Connected to /ws/message');
    
    // Send authentication message
    const authMessage = {
        user_id: "test_user_message"
    };
    console.log('🔐 Sending authentication:', authMessage);
    messageWs.send(JSON.stringify(authMessage));
};

messageWs.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('📨 Received from /ws/message:', data);
    
    if (data.status === 'authenticated') {
        console.log('✅ Authentication successful for user:', data.user_id);
        
        // Test sequence: broadcast -> private message -> another broadcast
        setTimeout(() => {
            // Send broadcast message
            const broadcastMessage = {
                type: "broadcast",
                content: "Hello everyone from message test!",
                timestamp: new Date().toISOString()
            };
            console.log('📤 Sending broadcast message:', broadcastMessage);
            messageWs.send(JSON.stringify(broadcastMessage));
        }, 1000);
        
        setTimeout(() => {
            // Send private message
            const privateMessage = {
                type: "private",
                target_user_id: "another_user",
                content: "This is a private message",
                timestamp: new Date().toISOString()
            };
            console.log('📤 Sending private message:', privateMessage);
            messageWs.send(JSON.stringify(privateMessage));
        }, 3000);
    }
    
    if (data.type === 'user_joined') {
        console.log('👋 User joined:', data.user_id);
    }
    
    if (data.type === 'message_status') {
        console.log('✅ Message delivery status:', data);
    }
};

messageWs.onclose = function() {
    console.log('❌ /ws/message connection closed');
};

messageWs.onerror = function(error) {
    console.log('⚠️ /ws/message error:', error);
};