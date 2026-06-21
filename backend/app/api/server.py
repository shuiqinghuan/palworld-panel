from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import ServerInfo, PlayerInfo, BackupInfo, CommandRequest, CommandResponse
from app.services import rcon_service, server_service
from datetime import datetime

router = APIRouter(prefix="/api/server", tags=["server"])


@router.get("/status", response_model=ServerInfo)
async def get_server_status():
    server_info = server_service.get_server_info()
    if not server_info:
        raise HTTPException(status_code=404, detail="Server is not running")
    
    players = await rcon_service.get_players()
    server_info.players_count = len(players)
    
    return server_info


@router.post("/start")
async def start_server():
    success = await server_service.start_server()
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start server")
    return {"message": "Server start command executed"}


@router.post("/stop")
async def stop_server():
    success = await server_service.stop_server()
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop server")
    return {"message": "Server stopped successfully"}


@router.get("/players", response_model=List[PlayerInfo])
async def get_players():
    players = await rcon_service.get_players()
    return players


@router.post("/kick/{steam_id}")
async def kick_player(steam_id: str, reason: str = ""):
    success = await rcon_service.kick_player(steam_id, reason)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to kick player")
    return {"message": f"Player {steam_id} kicked"}


@router.post("/ban/{steam_id}")
async def ban_player(steam_id: str, reason: str = ""):
    success = await rcon_service.ban_player(steam_id, reason)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to ban player")
    return {"message": f"Player {steam_id} banned"}


@router.post("/broadcast")
async def broadcast_message(message: str):
    success = await rcon_service.broadcast(message)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to broadcast message")
    return {"message": "Broadcast sent"}


@router.post("/save")
async def save_server():
    success = await rcon_service.save_server()
    if not success:
        raise HTTPException(status_code=400, detail="Failed to save server")
    return {"message": "Server saved"}


@router.post("/shutdown")
async def shutdown_server(seconds: int = 10, message: str = "Server is shutting down"):
    success = await rcon_service.shutdown_server(seconds, message)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to shutdown server")
    return {"message": f"Server will shutdown in {seconds} seconds"}


@router.post("/command", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    result = await rcon_service.execute_command(request.command)
    if result is None:
        return CommandResponse(
            success=False,
            message="Failed to execute command"
        )
    return CommandResponse(
        success=True,
        message="Command executed successfully",
        data={"result": result}
    )


@router.get("/backups", response_model=List[BackupInfo])
async def list_backups():
    backups = server_service.list_backups()
    return backups


@router.post("/backup")
async def create_backup(description: str = ""):
    backup = await server_service.create_backup(description)
    if not backup:
        raise HTTPException(status_code=500, detail="Failed to create backup")
    return backup


@router.post("/backup/{backup_id}/restore")
async def restore_backup(backup_id: str):
    success = await server_service.restore_backup(backup_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to restore backup")
    return {"message": f"Backup {backup_id} restored successfully"}


@router.delete("/backup/{backup_id}")
async def delete_backup(backup_id: str):
    success = await server_service.delete_backup(backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backup not found")
    return {"message": f"Backup {backup_id} deleted"}