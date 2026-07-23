from dataclasses import dataclass


@dataclass(frozen=True)
class Insight:
    key: str
    category: str
    title: str
    description: str
    score: float
