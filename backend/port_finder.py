import socket
from pathlib import Path


def find_free_port(start: int = 8000, end: int = 8010, port_file: str = "data/.port") -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                Path(port_file).parent.mkdir(parents=True, exist_ok=True)
                Path(port_file).write_text(str(port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free port found in range {start}-{end}")
