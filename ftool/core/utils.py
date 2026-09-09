import os
import sys
import platform
import psutil
from typing import Dict, Any

class SystemMonitor:
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(os.path.abspath(os.sep))
            return {
                "cpu_percent": cpu_percent,
                "ram_percent": mem.percent,
                "ram_used_gb": round(mem.used / (1024**3), 1),
                "ram_total_gb": round(mem.total / (1024**3), 1),
                "disk_percent": disk.percent,
                "python_version": platform.python_version(),
                "os_info": f"{platform.system()} {platform.release()}"
            }
        except Exception:
            return {
                "cpu_percent": 0.0,
                "ram_percent": 0.0,
                "ram_used_gb": 0.0,
                "ram_total_gb": 0.0,
                "disk_percent": 0.0,
                "python_version": platform.python_version(),
                "os_info": platform.system()
            }
