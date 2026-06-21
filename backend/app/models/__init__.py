from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ServerInfo(BaseModel):
    name: str
    version: str
    status: str
    uptime: Optional[int] = None
    players_count: int
    max_players: int
    cpu_usage: float
    memory_usage: float
    memory_total: float


class PlayerInfo(BaseModel):
    steam_id: str
    name: str
    level: Optional[int] = None
    location: Optional[str] = None
    ping: Optional[int] = None


class ServerConfig(BaseModel):
    server_name: str
    server_description: str
    admin_password: str
    server_password: str
    max_players: int
    public_port: int
    public_ip: str


class BackupInfo(BaseModel):
    id: str
    filename: str
    size: int
    created_at: datetime
    description: Optional[str] = None


class CommandRequest(BaseModel):
    command: str
    params: Optional[dict] = None


class CommandResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SystemStats(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used: float
    memory_total: float
    disk_percent: float
    disk_used: float
    disk_total: float
    network_sent: float
    network_recv: float