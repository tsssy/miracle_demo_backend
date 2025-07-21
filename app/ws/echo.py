from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            if data == "bye":
                # 收到 'bye' 主动断开连接
                await websocket.close()
                break
            await websocket.send_text(f"echo: {data}bbb")
    except WebSocketDisconnect:
        print("[ECHO] 客户端已断开连接") 