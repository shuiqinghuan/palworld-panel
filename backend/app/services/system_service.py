import psutil
from app.models import SystemStats
import logging

logger = logging.getLogger(__name__)


class SystemService:
    def get_system_stats(self) -> SystemStats:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            memory = psutil.virtual_memory()
            
            disk = psutil.disk_usage('/')
            
            network = psutil.net_io_counters()
            
            return SystemStats(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used / (1024 * 1024),
                memory_total=memory.total / (1024 * 1024),
                disk_percent=disk.percent,
                disk_used=disk.used / (1024 * 1024 * 1024),
                disk_total=disk.total / (1024 * 1024 * 1024),
                network_sent=network.bytes_sent / (1024 * 1024),
                network_recv=network.bytes_recv / (1024 * 1024)
            )
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return SystemStats(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used=0.0,
                memory_total=0.0,
                disk_percent=0.0,
                disk_used=0.0,
                disk_total=0.0,
                network_sent=0.0,
                network_recv=0.0
            )


system_service = SystemService()