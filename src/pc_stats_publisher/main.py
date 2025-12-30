from __future__ import annotations

import asyncio
import logging
import signal

from .config import Settings
from .server import MetricsPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger("pc-stats-opc-ua-publisher")


def _setup_signal_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()

    def _handle_signal() -> None:
        LOGGER.info("Shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_signal)
        except NotImplementedError:
            # Windows with older event loops may not support custom handlers.
            pass


async def _run() -> None:
    settings = Settings.from_env()
    publisher = MetricsPublisher(settings)
    stop_event = asyncio.Event()
    _setup_signal_handlers(stop_event)

    await publisher.start()
    LOGGER.info("OPC UA server listening at %s", settings.endpoint)

    try:
        await stop_event.wait()
    finally:
        await publisher.stop()
        LOGGER.info("Server stopped")


def main() -> None:
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        LOGGER.info("Interrupted by user")


if __name__ == "__main__":
    main()
