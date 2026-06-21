import asyncio
from typing import Optional, List
from valve.rcon import RCON
from app.config import settings
from app.models import PlayerInfo
import logging

logger = logging.getLogger(__name__)


class RCONService:
    def __init__(self):
        self.host = settings.RCON_HOST
        self.port = settings.RCON_PORT
        self.password = settings.RCON_PASSWORD
        self._connection = None
    
    async def connect(self) -> bool:
        try:
            self._connection = RCON((self.host, self.port), self.password)
            self._connection.connect()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RCON: {e}")
            return False
    
    async def disconnect(self):
        if self._connection:
            try:
                self._connection.close()
            except:
                pass
            self._connection = None
    
    async def execute_command(self, command: str) -> Optional[str]:
        try:
            if not self._connection:
                if not await self.connect():
                    return None
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._connection.request, 
                command
            )
            return result
        except Exception as e:
            logger.error(f"RCON command failed: {e}")
            await self.disconnect()
            return None
    
    async def get_players(self) -> List[PlayerInfo]:
        result = await self.execute_command("ShowPlayers")
        if not result:
            return []
        
        players = []
        lines = result.strip().split('\n')
        if len(lines) <= 1:
            return players
        
        for line in lines[1:]:
            parts = line.split(',')
            if len(parts) >= 2:
                player = PlayerInfo(
                    steam_id=parts[0],
                    name=parts[1],
                    level=int(parts[2]) if len(parts) > 2 else None
                )
                players.append(player)
        
        return players
    
    async def kick_player(self, steam_id: str, reason: str = "") -> bool:
        command = f"KickPlayer {steam_id}"
        if reason:
            command += f" {reason}"
        result = await self.execute_command(command)
        return result is not None
    
    async def ban_player(self, steam_id: str, reason: str = "") -> bool:
        command = f"BanPlayer {steam_id}"
        if reason:
            command += f" {reason}"
        result = await self.execute_command(command)
        return result is not None
    
    async def broadcast(self, message: str) -> bool:
        result = await self.execute_command(f"Broadcast {message}")
        return result is not None
    
    async def save_server(self) -> bool:
        result = await self.execute_command("Save")
        return result is not None
    
    async def shutdown_server(self, seconds: int = 10, message: str = "Server is shutting down") -> bool:
        result = await self.execute_command(f"Shutdown {seconds} {message}")
        return result is not None
    
    async def get_server_info(self) -> Optional[dict]:
        result = await self.execute_command("Info")
        if result:
            return {"info": result}
        return None


rcon_service = RCONService()