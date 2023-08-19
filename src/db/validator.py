from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


class DeviceType(BaseModel):
    name: str
    id: Optional[int] = None

    def __hash__(self):
        return hash(self.name)


class ConnectionType(BaseModel):
    src: str
    dst: str
    cost: float

    @field_validator("cost", mode="before")
    @classmethod
    def check_non_negative(cls, val: float):
        if val < 0:
            raise ValueError("Cost cannot be negative")
        return val

    @model_validator(mode="after")
    def check_self_loop(self) -> "ConnectionType":
        if self.src == self.dst:
            raise ValueError("Edge does not allow self-referencing")
        return self

    def __hash__(self):
        return hash(f"{self.src}_{self.dst}_{self.cost}")
