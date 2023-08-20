from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class DeviceType(BaseModel):
    name: str = Field(title="name of the device", max_length=30)
    id: Optional[int] = None

    def __hash__(self):
        return hash(self.name)


class ConnectionType(BaseModel):
    src: str = Field(title="source device of the edge", max_length=30)
    dst: str = Field(title="dest device of the edge", max_length=30)
    cost: float = Field(
        title="cost associated with the edge",
        ge=0,
        description="cost cannot be negative",
    )

    @model_validator(mode="after")
    def check_self_loop(self) -> "ConnectionType":
        if self.src == self.dst:
            raise ValueError("Edge does not allow self-referencing")
        return self

    def __hash__(self):
        return hash(f"{self.src}_{self.dst}_{self.cost}")
