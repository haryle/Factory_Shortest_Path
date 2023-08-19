import os
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import sessionmaker

from src.db.schema import Base, Connections, Devices
from src.db.validator import ConnectionType, DeviceType
from src.shortest_path import Controller

load_dotenv()

DATABASE = "mysql"
DIALECT = "mysqlconnector"
DB_USR = os.getenv("DB_USR")
DB_PASSWD = os.getenv("DB_PASSWD")
DB_ADDR = os.getenv("DB_ADDR")
DB_NAME = os.getenv("DB_NAME")

# Creat engine
engine = create_engine(f"{DATABASE}+{DIALECT}://{DB_USR}:{DB_PASSWD}@{DB_ADDR}/{DB_NAME}")

# Create session
Session = sessionmaker(engine)
Base.metadata.create_all(engine)
app = FastAPI()


@app.get("/devices")
def select_devices() -> List[DeviceType]:
    with Session() as session:
        select_stmt = select(Devices).order_by(Devices.id)
        result = session.scalars(select_stmt).all()
    return [DeviceType(**item.__dict__) for item in result]


@app.get("/connections")
def select_connections() -> List[ConnectionType]:
    with Session() as session:
        select_stmt = select(Connections)
        result = session.scalars(select_stmt).all()
    return [ConnectionType(**item.__dict__) for item in result]


@app.post("/add/devices/")
def upsert_devices(
    devices: DeviceType | List[DeviceType],
) -> List[Dict]:
    if isinstance(devices, DeviceType):
        devices = [devices]
    _devices = [device.model_dump() for device in devices]

    with Session() as session:
        insert_stmt = insert(Devices).values(_devices)
        upsert_stmt = insert_stmt.on_duplicate_key_update(
            name=insert_stmt.inserted.name,
        )
        try:
            session.execute(upsert_stmt)
            session.commit()
            print("UPSERT INTO DEVICES SUCCESSFUL")
        except Exception as e:
            print(f"UPSERT ERROR: {e}")
            session.rollback()
    return _devices


@app.post("/add/connections/")
def upsert_connections(
    connections: ConnectionType | List[ConnectionType],
) -> List[Dict]:
    if isinstance(connections, ConnectionType):
        connections = [connections]
    _connections = [con.model_dump() for con in connections]

    with Session() as session:
        insert_stmt = insert(Connections).values(_connections)
        upsert_stmt = insert_stmt.on_duplicate_key_update(
            cost=insert_stmt.inserted.cost,
        )
        try:
            session.execute(upsert_stmt)
            session.commit()
            print("UPSERT INTO CONNECTIONS SUCCESSFUL")
        except Exception as e:
            print(f"UPSERT ERROR: {e}")
            session.rollback()
    return _connections


@app.get("/path/")
def get_shortest_path(src: str = ...):
    controller = Controller(
        devices=select_devices(),
        connections=select_connections(),
    )
    return controller.get_best_path_from_source(src)
