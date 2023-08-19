import logging
import logging.config
import os
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import sessionmaker

from src.db.schema import Base, Connections, Devices
from src.db.validator import ConnectionType, DeviceType
from src.shortest_path import Controller

# Create log files
log_file_path = Path(__file__).parents[1] / "log"
normal_log = log_file_path / "normal.log"
error_log = log_file_path / "error.log"
normal_log.mkdir(parents=True, exist_ok=True)
error_log.mkdir(parents=True, exist_ok=True)

# Setup logging
log_conf_path = Path(__file__).parent / "logging_conf.yaml"
with open(log_conf_path, "r") as file:
    log_conf = yaml.load(file, Loader=yaml.FullLoader)
logging.config.dictConfig(log_conf)
logger = logging.getLogger(__name__)


# Load environment variables
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
def select_devices() -> Optional[List[DeviceType]]:
    logger.info("/devices API invoked")
    try:
        with Session() as session:
            select_stmt = select(Devices).order_by(Devices.id)
            logger.info(f"SQL stmt: {str(select_stmt)}")
            result = session.scalars(select_stmt).all()
        return [DeviceType(**item.__dict__) for item in result]
    except Exception as e:
        logger.error(f"ERROR for /devices: {e}")


@app.get("/connections")
def select_connections() -> Optional[List[ConnectionType]]:
    logger.info("/connections API invoked")
    try:
        with Session() as session:
            select_stmt = select(Connections)
            logger.info(f"SQL stmt: {str(select_stmt)}")
            result = session.scalars(select_stmt).all()
        return [ConnectionType(**item.__dict__) for item in result]
    except Exception as e:
        logger.error(f"ERROR for /connections: {e}")


@app.post("/add/devices/")
def upsert_devices(
    devices: DeviceType | List[DeviceType],
) -> List[Dict]:
    logger.info("/add/devices/ API invoked")
    if isinstance(devices, DeviceType):
        devices = [devices]
    _devices = [device.model_dump() for device in devices]

    with Session() as session:
        insert_stmt = insert(Devices).values(_devices)
        upsert_stmt = insert_stmt.on_duplicate_key_update(
            name=insert_stmt.inserted.name,
        )
        logger.info(f"SQL stmt: {upsert_stmt}")
        try:
            session.execute(upsert_stmt)
            session.commit()
            logger.info("Upsert into devices successful")
        except Exception as e:
            logger.error(f"ERROR /add/devices: {e}")
            session.rollback()
    return _devices


@app.post("/add/connections/")
def upsert_connections(
    connections: ConnectionType | List[ConnectionType],
) -> List[Dict]:
    logger.info("/add/connections/ API invoked")
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
            logger.info("Upsert into connections successful")
        except Exception as e:
            logger.error(f"ERROR /add/connections: {e}")
            session.rollback()
    return _connections


@app.get("/path/")
def get_shortest_path(src: str = ...):
    logger.info(f"/path/?src={src} API invoked")
    try:
        controller = Controller(
            devices=select_devices(),  # type: ignore
            connections=select_connections(),  # type: ignore
        )
        return controller.get_best_path_from_source(src)
    except Exception as e:
        logger.error(f"ERROR /path/?src={src}: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_config=str(log_conf_path))
