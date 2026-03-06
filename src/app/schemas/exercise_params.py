from pydantic import BaseModel, Field


class KneeExtensionV1Params(BaseModel):
    # Ângulo mínimo (flexão) e máximo (extensão) em graus
    low_deg: float = Field(95.0, ge=40.0, le=160.0)
    high_deg: float = Field(170.0, ge=120.0, le=200.0)

    # Histerese para evitar trepidação no limiar
    hysteresis_deg: float = Field(3.0, ge=0.0, le=15.0)

    # Tempo mínimo (ms) para confirmar cruzamento de limiar
    min_hold_ms: int = Field(80, ge=0, le=500)
