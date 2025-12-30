from __future__ import annotations

from dataclasses import dataclass
import os
import psutil

_PROCFS_PATH = os.getenv("PROCFS_PATH")
if _PROCFS_PATH:
    psutil.PROCFS_PATH = _PROCFS_PATH


@dataclass(frozen=True)
class SystemMetrics:
    cpu_percent: float
    memory_percent: float


def collect_metrics() -> SystemMetrics:
    """Gather CPU and memory utilization percentages."""
    cpu_percent = psutil.cpu_percent(interval=None)
    memory_percent = psutil.virtual_memory().percent
    return SystemMetrics(cpu_percent=cpu_percent, memory_percent=memory_percent)
