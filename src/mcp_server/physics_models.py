from pydantic import BaseModel, Field, field_validator

class TsiolkovskyInput(BaseModel):
    delta_v: float = Field(..., description="Required delta-v in meters per second (m/s)")
    exhaust_velocity: float = Field(..., description="Effective exhaust velocity in meters per second (m/s)")
    payload_mass: float = Field(..., description="Mass of the payload in kilograms (kg)")
    structural_ratio: float = Field(0.1, description="Estimated structural mass fraction (0 to 1)")

    @field_validator('delta_v', 'exhaust_velocity', 'payload_mass')
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Physical constraints violated: Value must be strictly greater than 0.")
        return v
    
    @field_validator('structural_ratio')
    @classmethod
    def valid_structural_ratio(cls, v: float) -> float:
        if not (0.0 < v < 1.0):
            raise ValueError("Structural ratio must be between 0.0 and 1.0")
        return v
