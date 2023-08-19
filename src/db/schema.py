from typing import List

from sqlalchemy import (
    CheckConstraint,
    Column,
    Computed,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    column_property,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Devices(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    # Defining relationship
    # A device name can appear as either src or dst in connections table
    connections_src: Mapped[List["Connections"]] = relationship(
        back_populates="devices_src",
        cascade="all, delete-orphan",
        foreign_keys="Connections.src",
    )

    connections_dst: Mapped[List["Connections"]] = relationship(
        back_populates="devices_dst",
        cascade="all, delete-orphan",
        foreign_keys="Connections.dst",
    )


class Connections(Base):
    __tablename__ = "connections"

    src: Mapped[str] = mapped_column(
        ForeignKey("devices.name"),
        nullable=False,
        primary_key=True,
    )
    dst: Mapped[str] = mapped_column(
        ForeignKey("devices.name"),
        nullable=False,
        primary_key=True,
    )
    cost: Mapped[float] = mapped_column(Float(6))

    # Defining relationships:
    # src and dst are foreign keys referencing name in devices
    devices_src: Mapped["Devices"] = relationship(
        back_populates="connections_src",
        foreign_keys="Connections.src",
    )

    devices_dst: Mapped["Devices"] = relationship(
        back_populates="connections_dst",
        foreign_keys="Connections.dst",
    )

    # Virtual generated fields - computed from the server side
    pair_min = column_property(Column(String(30), Computed("LEAST(src,dst)")))
    pair_max = column_property(Column(String(30), Computed("GREATEST(src,dst)")))

    # Defining Constraints
    __table_args__ = (
        CheckConstraint(  # Cost cannot be negative
            "cost>0",
            "non_negative_cost",
        ),
        CheckConstraint(  # No self loop allowed
            "first<>second",
            "non_self_loop",
        ),
        # Only one permutation of (first, second) allowed
        # Define unidirected edge
        Index("unidirected", pair_min, pair_max, unique=True),
    )
