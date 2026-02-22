#!/usr/bin/env python3
"""
Mattermost Custom Client with WebSocket real-time messaging
"""

import asyncio
import json
import aiohttp
import websockets
from typing import Optional, Callable


class MattermostClient:
    def __init__(self, server_url: str, token: str, timeout: int = 30):
        """
        Args:
            server_url: e.g. "https://mattermost.example.com"
            token: Personal Access Token or session token
        """
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.seq = 1
        self.running = False

    async def _get_auth_headers(self) -> dict:
        """Get authorization headers for REST API calls"""
        return {"Authorization": f"Bearer {self.token}"}

    async def connect_websocket(self):
        """Connect to Mattermost WebSocket"""
        ws_url = f"{self.server_url}/api/v4/websocket"
        self.ws = await websockets.connect(ws_url)
        print(f"Connected to {ws_url}")
        
        # Authenticate via hello event
        auth_data = {
            "seq": 1,
            "action": "authentication_challenge",
            "data": {"token": self.token}
        }
        await self.ws.send(json.dumps(auth_data))

    async def send(self, action: str, data: dict, timeout: Optional[int] = None):
        """Send a WebSocket message and wait for response"""
        timeout = timeout or self.timeout
        seq_id = self.seq
        self.seq += 1
        
        msg = {
            "seq": seq_id,
            "action": action,
            "data": data
        }
        
        await self.ws.send(json.dumps(msg))
        
        # Wait for response with matching seq
        for _ in range(timeout * 10):
            response = await asyncio.wait_for(self.ws.recv(), timeout=0.1)
            resp_data = json.loads(response)
            if resp_data.get("seq_reply") == seq_id or resp_data.get("seq") == seq_id:
                return resp_data
            elif resp_data.get("event") == "hello":
                continue  # Skip hello events
        
        raise TimeoutError(f"No response for {action}")

    async def get_user_info(self) -> dict:
        """Get current user info via REST API"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.server_url}/api/v4/users/me",
                headers=await self._get_auth_headers()
            ) as resp:
                return await resp.json()

    async def get_channels(self) -> list:
        """Get channels the user belongs to"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.server_url}/api/v4/channels",
                headers=await self._get_auth_headers()
            ) as resp:
                return await resp.json()

    async def get_channel_id(self, channel_name: str, team_id: str = None) -> str:
        """Get channel ID by name"""
        async with aiohttp.ClientSession() as session:
            params = {"name": channel_name}
            if team_id:
                params["team_id"] = team_id
                
            async with session.get(
                f"{self.server_url}/api/v4/channels/name/{channel_name}",
                headers=await self._get_auth_headers(),
                params=params
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["id"]
                raise ValueError(f"Channel {channel_name} not found")

    async def send_message(self, channel_id: str, message: str) -> dict:
        """Send a message to a channel via REST API"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "channel_id": channel_id,
                "message": message
            }
            async with session.post(
                f"{self.server_url}/api/v4/posts",
                json=payload,
                headers=await self._get_auth_headers()
            ) as resp:
                return await resp.json()

    async def get_posts(self, channel_id: str, limit: int = 20) -> list:
        """Get posts from a channel"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.server_url}/api/v4/channels/{channel_id}/posts",
                params={"limit_per_page": limit},
                headers=await self._get_auth_headers()
            ) as resp:
                data = await resp.json()
                return list(data.get("posts", {}).values())

    async def listen(self, message_handler: Callable[[dict], None]):
        """
        Listen for real-time events
        
        Args:
            message_handler: Callback function that receives event data
        """
        self.running = True
        while self.running:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                data = json.loads(message)
                
                # Handle different event types
                event_type = data.get("event", "")
                
                if event_type == "posted":
                    message_handler(data.get("data", {}))
                elif event_type == "hello":
                    print("WebSocket authenticated successfully")
                elif event_type == "error":
                    print(f"Server error: {data.get('data', {})}")
                else:
                    print(f"Event: {event_type}")
                    
            except asyncio.TimeoutError:
                continue
            except websockets.ConnectionClosed:
                print("Connection closed, reconnecting...")
                await asyncio.sleep(5)
                try:
                    await self.connect_websocket()
                except:
                    continue

    async def close(self):
        """Close the connection"""
        self.running = False
        if self.ws:
            await self.ws.close()


async def example_usage():
    """Example of how to use the client"""
    
    # 配置
    SERVER_URL = "https://your-mattermost-server.com"
    TOKEN = "your-personal-access-token"
    
    # 创建客户端
    client = MattermostClient(SERVER_URL, TOKEN)
    
    # 连接 WebSocket
    await client.connect_websocket()
    
    # 获取用户信息
    user = await client.get_user_info()
    print(f"Logged in as: {user.get('username')} ({user.get('email')})")
    
    # 获取频道列表
    channels = await client.get_channels()
    print(f"Available channels: {len(channels)}")
    for ch in channels[:5]:
        print(f"  - {ch.get('display_name')} ({ch.get('name')})")
    
    # 处理新消息
    def handle_message(data):
        print(f"\n📨 New message received:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 开始监听（实际使用时建议后台运行）
    # await client.listen(handle_message)
    
    # 示例：发送消息（取消注释测试）
    # channel_id = "target-channel-id"
    # await client.send_message(channel_id, "Hello from Mattermost Client!")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
