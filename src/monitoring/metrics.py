from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ApiMetrics:
    prediction_count: int = 0
    batch_prediction_count: int = 0
    health_check_count: int = 0
    risk_tier_counts: dict[str, int] = field(default_factory=dict)
    score_sum: float = 0.0
    score_min: float | None = None
    score_max: float | None = None
    recent_scores: list[float] = field(default_factory=list)

    def record_prediction(self, tier: str, probability: float, batch_size: int = 1) -> None:
        self.prediction_count += batch_size
        self.risk_tier_counts[tier] = self.risk_tier_counts.get(tier, 0) + batch_size
        self.score_sum += probability
        self.score_min = probability if self.score_min is None else min(self.score_min, probability)
        self.score_max = probability if self.score_max is None else max(self.score_max, probability)
        self.recent_scores = [*self.recent_scores, probability][-100:]

    def record_batch(self, batch_size: int) -> None:
        self.batch_prediction_count += 1

    def as_dict(self) -> dict[str, object]:
        return {
            "prediction_count": self.prediction_count,
            "batch_prediction_count": self.batch_prediction_count,
            "health_check_count": self.health_check_count,
            "risk_tier_counts": self.risk_tier_counts,
            "score_distribution": {
                "average": self.score_sum / self.prediction_count if self.prediction_count else None,
                "min": self.score_min,
                "max": self.score_max,
                "recent_count": len(self.recent_scores),
            },
        }
