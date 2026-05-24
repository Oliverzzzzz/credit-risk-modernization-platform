from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ApiMetrics:
    prediction_count: int = 0
    batch_prediction_count: int = 0
    health_check_count: int = 0
    risk_tier_counts: dict[str, int] = field(default_factory=dict)

    def record_prediction(self, tier: str, batch_size: int = 1) -> None:
        self.prediction_count += batch_size
        self.risk_tier_counts[tier] = self.risk_tier_counts.get(tier, 0) + batch_size

    def record_batch(self, batch_size: int) -> None:
        self.batch_prediction_count += 1

    def as_dict(self) -> dict[str, object]:
        return {
            "prediction_count": self.prediction_count,
            "batch_prediction_count": self.batch_prediction_count,
            "health_check_count": self.health_check_count,
            "risk_tier_counts": self.risk_tier_counts,
        }
