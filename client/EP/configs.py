from dataclasses import dataclass

@dataclass
class _Config:
    API_BASE = "ws://bmlm.win/ws"
    VIEWER_PORT = 33601


Config = _Config()