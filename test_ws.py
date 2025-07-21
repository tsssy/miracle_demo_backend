import asyncio
import websockets
import json

async def test_ws():
    # WebSocket 服务端地址（请根据实际端口和路由修改）
    uri = "ws://localhost:8000/ws/chat"
    print("链接钱")
    # 连接 WebSocket 服务端
    async with websockets.connect(uri) as ws:
        print("已连接到服务器")

        # 1. 发送认证信息（必须与服务端 ConnectionHandler._authenticate 逻辑一致）
        auth_data = {"user_id": "1000000"}
        await ws.send(json.dumps(auth_data))
        print("已发送认证信息:", auth_data)

        # 2. 发送一条普通消息
        await ws.send("你好，WebSocket！")
        print("已发送普通消息")

        # 3. 循环接收服务器消息
        try:
            while True:
                msg = await ws.recv()
                print("收到服务器消息:", msg)
        except websockets.ConnectionClosed:
            print("连接已关闭")

if __name__ == "__main__":
    asyncio.run(test_ws()) 