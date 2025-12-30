from __future__ import annotations

import asyncio
from asyncua import Server

from .config import Settings
from .metrics import SystemMetrics, collect_metrics


class MetricsPublisher:
    """OPC UA server that periodically publishes CPU and RAM usage."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._server = Server()
        self._update_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self._cpu_node = None
        self._ram_node = None

    async def start(self) -> None:
        await self._server.init()
        self._server.set_endpoint(self._settings.endpoint)
        namespace_idx = await self._server.register_namespace(self._settings.namespace_uri)

        objects_node = self._server.get_objects_node()
        metrics_node = await objects_node.add_object(namespace_idx, "SystemMetrics")
        self._cpu_node = await metrics_node.add_variable(
            namespace_idx, "CPUUsagePercent", 0.0
        )
        self._ram_node = await metrics_node.add_variable(
            namespace_idx, "MemoryUsagePercent", 0.0
        )

        await self._cpu_node.set_writable(False)
        await self._ram_node.set_writable(False)

        await self._server.start()
        self._update_task = asyncio.create_task(self._update_loop())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        await self._server.stop()

    async def _update_loop(self) -> None:
        try:
            while not self._stop_event.is_set():
                metrics = collect_metrics()
                await self._write_metrics(metrics)

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self._settings.update_interval_seconds,
                    )
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            raise

    async def _write_metrics(self, metrics: SystemMetrics) -> None:
        if not self._cpu_node or not self._ram_node:
            raise RuntimeError("Server nodes have not been initialized")
        await self._cpu_node.write_value(round(metrics.cpu_percent, 2))
        await self._ram_node.write_value(round(metrics.memory_percent, 2))

    async def run_until_stopped(self) -> None:
        await self._stop_event.wait()
