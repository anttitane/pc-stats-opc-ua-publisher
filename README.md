# pc-stats-opc-ua-publisher
Python OPC UA server that publishes the host's CPU and RAM usage percentages. Works on both Windows and Ubuntu hosts and can be containerized via Docker.

## Features
 - Periodically samples CPU and RAM utilization using `psutil`
 - Exposes metrics via an OPC UA namespace for easy consumption by industrial clients
 - Configurable endpoint, namespace, and sampling interval through environment variables
 - Runs natively with Python or inside Docker for consistent deployments

## Getting Started

### 1. Local Python run
```bash
python -m venv .venv
.\.venv\Scripts\activate   # use source .venv/bin/activate on Linux/macOS
pip install -e .
python -m pc_stats_publisher.main
```

The server listens on `opc.tcp://0.0.0.0:4840/pc-stats/` by default.

### 2. Docker build and run
```bash
docker build -t pc-stats-opc-ua-publisher .
docker run --rm -p 4840:4840 pc-stats-opc-ua-publisher
```

Override config at runtime, e.g.:
```bashp
docker run --rm -p 4880:4880 \
	-e OPCUA_ENDPOINT_PORT=4880 \
	-e OPCUA_UPDATE_INTERVAL_SECONDS=1.0 \
	pc-stats-opc-ua-publisher
```

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `OPCUA_ENDPOINT_HOST` | `0.0.0.0` | Interface to bind OPC UA endpoint |
| `OPCUA_ENDPOINT_PORT` | `4840` | TCP port for the OPC UA server |
| `OPCUA_NAMESPACE_URI` | `urn:pc-stats-opc-ua-publisher` | Namespace identifier for metrics |
| `OPCUA_UPDATE_INTERVAL_SECONDS` | `2.0` | Sampling cadence for CPU/RAM metrics |
| `PROCFS_PATH` | *(unset)* | Optional override so psutil reads host `/proc` (Linux) |

## OPC UA Address Space
 - Object: `SystemMetrics`
	 - Variable: `CPUUsagePercent`
	 - Variable: `MemoryUsagePercent`

Both values are reported as floats rounded to two decimals.

## Capturing host metrics from Docker (Linux)

To expose the real host CPU/RAM while running in a container, bind-mount the host `/proc` and join the host PID namespace:

```bash
docker run --rm \
	--pid=host --net=host --privileged \
	-v /proc:/proc_host:ro \
	-e PROCFS_PATH=/proc_host \
	pc-stats-opc-ua-publisher
```

`PROCFS_PATH` tells `psutil` which `/proc` root to read from. The `--privileged` flag (or an equivalent set of capabilities) is required because accessing the host namespaces is sensitive; only do this on trusted Linux hosts. Windows hosts do not offer this mechanism—run the publisher directly on Windows if you need Windows host metrics.
