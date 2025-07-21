from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/upper")
async def websocket_upper(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            if data == "bye":
                # 收到 'bye' 主动断开连接
                await websocket.close()
                break
            upper_data = data.upper()
            await websocket.send_text(f"upper: {upper_data}")
    except WebSocketDisconnect:
        print("[UPPER] 客户端已断开连接") 