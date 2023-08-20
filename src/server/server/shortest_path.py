"""
Implements Djisktra Shortest Path Algorithm 

Some of the limitations: 

- Does not exclude paths that are currently in use. 
- Implements a k-shortest path algorithm where k = 1 

TODO: 

- Connects to database with Mysql 
- Implements the full k-shortest path algorithm 
"""

from typing import Annotated, Any, Dict, List, Tuple, Union

from pydantic import BaseModel, computed_field, model_validator
from pydantic.functional_validators import BeforeValidator
from validator import ConnectionType, DeviceType

EdgeDict = Dict[Tuple[str, str], float]
BestDist = Dict[str, float]
BestPrev = Dict[str, int]
BestPathOutput = Tuple[BestDist, BestPrev]

INF = 100000
NULL = "NULL"


def check_non_negative_edge_cost(
    edges: List[ConnectionType],
    **kwargs,
) -> List[ConnectionType]:
    for item in edges:
        if item.cost < 0:
            raise ValueError(f"Edge cost must be non-negative: {item}")
    return edges


def check_duplicated_edge(
    edges: List[ConnectionType],
    **kwargs,
) -> EdgeDict:
    """Validate input edges, raises error if

    - there is a self-loop i.e. (1,1, 0.0)
    - there is a redefinition - i.e.
        - old: (1,2,3)
        - new: (1,2,4)
    - there is a bidirectional edge - i.e.
        - old: (1,2,3)
        - new: (2,1,3)

    Args:
        edges (List[Tuple[int, int, float]]): list of edges and cost

    Raises:
        ValueError: if there is a self-loop
        ValueError: if there is a redefinition or bidirectional edge

    Returns:
        Dict[Tuple[int,int], float]: mapping of edges to costs
    """
    edge_dict = {}
    for item in edges:
        if item.src == item.dst:
            raise ValueError(f"Controller does not allow self-loop: {item}")
        first = item.src
        second = item.dst
        value = item.cost
        if (first, second) not in edge_dict:
            edge_dict[first, second] = value
        else:
            old_value = edge_dict[first, second]
            if old_value != value:
                raise ValueError(f"A previous edge was defined with value: {first, second, old_value}")
        if (second, first) in edge_dict:
            raise ValueError(f"Edge cannot be bidirectional: {item}")
    return edge_dict


def coerce_to_ConnectionType(
    cons: Union[
        List[Tuple[str, str, float]],
        List[Dict],
        List[ConnectionType],
    ],
    **kwargs,
) -> List[ConnectionType]:
    result = []
    for item in cons:
        if isinstance(item, tuple):
            result.append(
                ConnectionType(
                    src=item[0],
                    dst=item[1],
                    cost=item[2],
                )
            )
        elif isinstance(item, Dict):
            result.append(ConnectionType(**item))
        elif isinstance(item, ConnectionType):
            result.append(item)
        else:
            raise ValueError("Invalid type.")
    return result


def coerce_to_DeviceType(
    devices: Union[
        List[str],
        List[Dict],
        List[DeviceType],
    ],
    **kwargs,
) -> List[DeviceType]:
    result = []
    for item in devices:
        if isinstance(item, str):
            result.append(DeviceType(name=item))
        elif isinstance(item, Dict):
            result.append(DeviceType(**item))
        elif isinstance(item, DeviceType):
            result.append(item)
        else:
            raise ValueError("Invalid type.")
    return result


ValidDevices = Annotated[List[DeviceType], BeforeValidator(coerce_to_DeviceType)]


class Controller(BaseModel):
    devices: Union[
        List[str],
        List[Dict],
        List[DeviceType],
    ]
    connections: Union[
        List[Tuple[str, str, float]],
        List[Dict],
        List[ConnectionType],
    ]

    @computed_field
    @property
    def Connections(self) -> EdgeDict:
        return check_duplicated_edge(
            check_non_negative_edge_cost(
                coerce_to_ConnectionType(
                    self.connections,
                ),
            ),
        )

    @computed_field
    @property
    def Devices(self) -> List[DeviceType]:
        return coerce_to_DeviceType(self.devices)

    @model_validator(mode="after")
    def validate_connections_nodes_in_devices(self) -> Any:
        defined = set(self.Devices)

        connection_nodes = set()

        for item in self.Connections:
            connection_nodes.add(DeviceType(name=item[0]))
            connection_nodes.add(DeviceType(name=item[1]))

        undefined = connection_nodes - defined
        for node in undefined:
            self.Devices.append(node)

    def get_neighbors(self, src: str | DeviceType) -> List[str]:
        if isinstance(src, str):
            src = DeviceType(name=src)
        devices = [item.name for item in self.Devices]
        if src.name not in devices:
            raise ValueError(f"Source was not previously defined: {src.name}")
        return [node.name for node in self.Devices if (src.name, node.name) in self.Connections]

    def get_best_path_from_source(self, src: str | DeviceType) -> Dict:
        if isinstance(src, str):
            src = DeviceType(name=src)
        devices = [item.name for item in self.Devices]
        if src.name not in devices:
            raise ValueError(f"Source not was not previously defined: {src}")

        dist = {}
        prev = {}
        proc_nodes = []
        for item in self.Devices:
            dist[item.name] = INF
            prev[item.name] = NULL
            proc_nodes.append(item.name)
        dist[src.name] = 0

        while len(proc_nodes) != 0:
            # Find vertex with min distance
            best_path = {k: dist[k] for k in proc_nodes}
            best_path = dict(sorted(best_path.items(), key=lambda item: item[1]))
            item = list(best_path.keys())[0]

            # Remove that vertex from processing nodes
            proc_nodes.remove(item)

            # Iterate through neighbours of item that is still being processed
            remaining_neighbours = set(self.get_neighbors(item)).intersection(set(proc_nodes))
            for neighbor in remaining_neighbours:
                new_dist = best_path[item] + self.Connections[item, neighbor]
                if new_dist < best_path[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = item
        return {"Cost": dist, "Parent": prev}
