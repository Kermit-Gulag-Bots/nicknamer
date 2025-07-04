from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RevealConfig:
    insult: str
    role_to_complain_to: str


@dataclass
class ServerConfig:
    reveal_config: Optional[RevealConfig]
    kermit_config: Optional[Dict]
