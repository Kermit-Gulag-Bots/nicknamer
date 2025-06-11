from dataclasses import dataclass
from typing import Dict


@dataclass
class RevealConfig:
    insult: str
    role_to_complain_to: str
    identities: Dict[int, str]


@dataclass
class IdentityConfig:
    reveal_config: RevealConfig
