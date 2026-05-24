from dataclasses import dataclass


@dataclass(frozen=True)
class RiskThresholds:
    low_max: float = 0.25
    medium_max: float = 0.55


@dataclass(frozen=True)
class ModelConfig:
    target_column: str = "default_flag"
    model_version: str = "baseline-0.1.0"
    random_state: int = 42
    test_size: float = 0.25
    thresholds: RiskThresholds = RiskThresholds()


DEFAULT_MODEL_CONFIG = ModelConfig()
