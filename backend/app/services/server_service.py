import os
import subprocess
import psutil
from typing import Optional, List
from datetime import datetime
from app.config import settings
from app.models import ServerInfo, BackupInfo
import logging
import shutil

logger = logging.getLogger(__name__)


class ServerService:
    def __init__(self):
        self.server_dir = settings.PALWORLD_SERVER_DIR
        self.executable_path = os.path.join(
            self.server_dir, 
            settings.PALWORLD_SERVER_EXECUTABLE
        )
        self.save_dir = os.path.join(self.server_dir, settings.PALWORLD_SAVE_DIR)
        self.backup_dir = settings.BACKUP_DIR
        self._process = None
    
    def is_server_running(self) -> bool:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'PalServer' in ' '.join(proc.info.get('cmdline', [])):
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking server status: {e}")
            return False
    
    def get_server_process(self) -> Optional[psutil.Process]:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'PalServer' in ' '.join(proc.info.get('cmdline', [])):
                    return proc
            return None
        except Exception as e:
            logger.error(f"Error getting server process: {e}")
            return None
    
    async def start_server(self) -> bool:
        if self.is_server_running():
            logger.warning("Server is already running")
            return False
        
        try:
            subprocess.Popen(
                [self.executable_path],
                cwd=self.server_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            logger.info("Server start command executed")
            return True
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    async def stop_server(self) -> bool:
        process = self.get_server_process()
        if not process:
            logger.warning("Server is not running")
            return False
        
        try:
            process.terminate()
            process.wait(timeout=10)
            logger.info("Server stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop server: {e}")
            try:
                process.kill()
                return True
            except:
                return False
    
    def get_server_info(self) -> Optional[ServerInfo]:
        process = self.get_server_process()
        if not process:
            return None
        
        try:
            cpu_percent = process.cpu_percent(interval=1)
            memory_info = process.memory_info()
            
            return ServerInfo(
                name="Palworld Server",
                version="1.0.0",
                status="running",
                uptime=int(process.create_time()),
                players_count=0,
                max_players=32,
                cpu_usage=cpu_percent,
                memory_usage=memory_info.rss / (1024 * 1024),
                memory_total=psutil.virtual_memory().total / (1024 * 1024)
            )
        except Exception as e:
            logger.error(f"Error getting server info: {e}")
            return None
    
    async def create_backup(self, description: str = "") -> Optional[BackupInfo]:
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"palworld_backup_{timestamp}.tar.gz"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            shutil.make_archive(
                backup_path.replace('.tar.gz', ''),
                'gztar',
                self.save_dir
            )
            
            backup_size = os.path.getsize(backup_path)
            
            backup_info = BackupInfo(
                id=timestamp,
                filename=backup_filename,
                size=backup_size,
                created_at=datetime.now(),
                description=description
            )
            
            await self._cleanup_old_backups()
            
            return backup_info
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    async def restore_backup(self, backup_id: str) -> bool:
        backup_path = os.path.join(self.backup_dir, f"palworld_backup_{backup_id}.tar.gz")
        
        if not os.path.exists(backup_path):
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        try:
            if self.is_server_running():
                await self.stop_server()
            
            shutil.unpack_archive(backup_path, self.save_dir)
            logger.info(f"Backup restored: {backup_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith("palworld_backup_") and filename.endswith(".tar.gz"):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                
                timestamp = filename.replace("palworld_backup_", "").replace(".tar.gz", "")
                
                backups.append(BackupInfo(
                    id=timestamp,
                    filename=filename,
                    size=stat.st_size,
                    created_at=datetime.fromtimestamp(stat.st_ctime)
                ))
        
        return sorted(backups, key=lambda x: x.created_at, reverse=True)
    
    async def delete_backup(self, backup_id: str) -> bool:
        backup_path = os.path.join(self.backup_dir, f"palworld_backup_{backup_id}.tar.gz")
        
        if not os.path.exists(backup_path):
            return False
        
        try:
            os.remove(backup_path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False
    
    async def _cleanup_old_backups(self):
        backups = self.list_backups()
        if len(backups) > settings.MAX_BACKUPS:
            for backup in backups[settings.MAX_BACKUPS:]:
                await self.delete_backup(backup.id)


server_service = ServerService()