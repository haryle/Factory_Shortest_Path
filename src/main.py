import os
from typing import Dict, List

from dotenv import load_dotenv
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


# TODO: Make it so that controller is a class attribute
# and gets updated at every new upsert. The expensive select
# should only be called at init
class Program:
    def __init__(self):
        Base.metadata.create_all(engine)

    def select_devices(self, Session=Session) -> List[DeviceType]:
        with Session() as session:
            select_stmt = select(Devices).order_by(Devices.id)
            result = session.scalars(select_stmt).all()
        return [DeviceType(**item.__dict__) for item in result]

    def select_connections(self, Session=Session) -> List[ConnectionType]:
        with Session() as session:
            select_stmt = select(Connections)
            result = session.scalars(select_stmt).all()
        return [ConnectionType(**item.__dict__) for item in result]

    def upsert_devices(self, devices: Dict | List[Dict]) -> None:
        if isinstance(devices, Dict):
            devices = [devices]
        _devices = [DeviceType(**device).model_dump() for device in devices]

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

    def upsert_connections(self, connections: Dict | List[Dict]) -> None:
        if isinstance(connections, Dict):
            connections = [connections]
        _connections = [ConnectionType(**con).model_dump() for con in connections]

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

    def get_shortest_path(self, src: str, Session=Session):
        controller = Controller(
            devices=self.select_devices(Session),
            connections=self.select_connections(Session),
        )
        return controller.get_best_path_from_source(src)


if __name__ == "__main__":
    p = Program()
    p.upsert_devices(
        [
            {"name": "A"},
            {"name": "B"},
            {"name": "C"},
            {"name": "D"},
        ]
    )
    p.upsert_connections(
        [
            {"src": "A", "dst": "B", "cost": 24},
            {"src": "A", "dst": "B", "cost": 24},
            {"src": "A", "dst": "C", "cost": 3},
            {"src": "A", "dst": "D", "cost": 20},
            {"src": "C", "dst": "D", "cost": 12},
        ],
    )
    result = p.get_shortest_path("A")
    print(f"BEST COSTS: {result[0]}")
    print(f"BEST PATHS: {result[1]}")
