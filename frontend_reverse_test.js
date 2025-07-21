// 连接到 /ws/reverse WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/reverse');

// 当连接打开时
ws.onopen = function() {
    console.log('已连接到 /ws/reverse');
    // 发送测试消息
    ws.send('reverse test!');
};

// 接收到消息时
ws.onmessage = function(event) {
    console.log('收到消息:', event.data);
};

// 连接关闭时
ws.onclose = function() {
    console.log('连接已关闭');
};

// 发生错误时
ws.onerror = function(error) {
    console.log('发生错误:', error);
}; 