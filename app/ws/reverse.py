from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/reverse")
async def websocket_reverse(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            if data == "bye":
                # 收到 'bye' 主动断开连接
                await websocket.close()
                break
            reversed_data = data[::-1]
            await websocket.send_text(f"reverse: {reversed_data}")
    except WebSocketDisconnect:
        print("[REVERSE] 客户端已断开连接") 