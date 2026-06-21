from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    APP_NAME: str = "Palworld Server Panel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    PALWORLD_SERVER_DIR: str = "/home/steam/palworld-server"
    PALWORLD_SERVER_EXECUTABLE: str = "Pal/Binaries/Linux/PalServer-Linux-Shipping"
    PALWORLD_SAVE_DIR: str = "Pal/Saved"
    
    RCON_HOST: str = "127.0.0.1"
    RCON_PORT: int = 25575
    RCON_PASSWORD: str = "adminpassword"
    
    BACKUP_DIR: str = "/var/backups/palworld"
    MAX_BACKUPS: int = 10
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/palworld_panel.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()