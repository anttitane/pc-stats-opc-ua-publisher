from __future__ import annotations

from dataclasses import dataclass
import os


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        raise ValueError(f"Environment variable {name} must be a number") from None


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"Environment variable {name} must be an integer") from None


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the OPC UA publisher."""

    endpoint_host: str = "0.0.0.0"
    endpoint_port: int = 4840
    namespace_uri: str = "urn:pc-stats-opc-ua-publisher"
    update_interval_seconds: float = 2.0

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            endpoint_host=os.getenv("OPCUA_ENDPOINT_HOST", cls.endpoint_host),
            endpoint_port=_env_int("OPCUA_ENDPOINT_PORT", cls.endpoint_port),
            namespace_uri=os.getenv("OPCUA_NAMESPACE_URI", cls.namespace_uri),
            update_interval_seconds=_env_float(
                "OPCUA_UPDATE_INTERVAL_SECONDS", cls.update_interval_seconds
            ),
        )

    @property
    def endpoint(self) -> str:
        return f"opc.tcp://{self.endpoint_host}:{self.endpoint_port}/pc-stats/"
