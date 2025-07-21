// Test script for /ws/match WebSocket handler
console.log('Testing /ws/match WebSocket connection...');

const matchWs = new WebSocket('ws://localhost:8000/ws/match');

matchWs.onopen = function() {
    console.log('✅ Connected to /ws/match');
    
    // Send authentication message
    const authMessage = {
        user_id: "test_user_match"
    };
    console.log('🔐 Sending authentication:', authMessage);
    matchWs.send(JSON.stringify(authMessage));
};

matchWs.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('📨 Received from /ws/match:', data);
    
    if (data.status === 'authenticated') {
        console.log('✅ Authentication successful for user:', data.user_id);
        
        // Start matching process
        setTimeout(() => {
            const startMatchMessage = {
                type: "start_matching"
            };
            console.log('🔍 Starting matching process:', startMatchMessage);
            matchWs.send(JSON.stringify(startMatchMessage));
        }, 1000);
    }
    
    if (data.type === 'match_system_connected') {
        console.log('🎯 Connected to match system:', data.message);
    }
    
    if (data.type === 'match_status') {
        console.log('📊 Match status:', data.status);
        
        if (data.status === 'waiting_for_match') {
            console.log('⏳ Waiting for another user to match...');
            
            // Simulate stopping matching after 5 seconds
            setTimeout(() => {
                const stopMatchMessage = {
                    type: "stop_matching"
                };
                console.log('🛑 Stopping matching:', stopMatchMessage);
                matchWs.send(JSON.stringify(stopMatchMessage));
            }, 5000);
        }
    }
    
    if (data.type === 'match_found') {
        console.log('🎉 Match found! Partner:', data.partner_id, 'Match ID:', data.match_id);
        
        // Send a message in the match
        setTimeout(() => {
            const matchMessage = {
                type: "match_message",
                content: "Hi there! Nice to meet you!",
                timestamp: new Date().toISOString()
            };
            console.log('💬 Sending match message:', matchMessage);
            matchWs.send(JSON.stringify(matchMessage));
        }, 2000);
        
        // End the match after some time
        setTimeout(() => {
            const endMatchMessage = {
                type: "end_match"
            };
            console.log('👋 Ending match:', endMatchMessage);
            matchWs.send(JSON.stringify(endMatchMessage));
        }, 10000);
    }
    
    if (data.type === 'match_message') {
        console.log('💬 Message from partner:', data.from, '-', data.content);
    }
    
    if (data.type === 'match_ended') {
        console.log('🏁 Match ended by:', data.ended_by);
    }
};

matchWs.onclose = function() {
    console.log('❌ /ws/match connection closed');
};

matchWs.onerror = function(error) {
    console.log('⚠️ /ws/match error:', error);
};