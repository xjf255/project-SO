from typing import Optional
from dataclasses import dataclass
@dataclass
class QueueConfig:
    name: str
    quantum: Optional[int] = None
    priority: int = 0  # Lower number = higher priority