import pytest
from pytest import fixture

from src.shortest_path import Controller


@fixture(scope="function")
def graph_nodes():
    return ["A", "B"]


@fixture(scope="function")
def self_loop_edges():
    return [("A", "B", 3), ("A", "A", 9)]


@fixture(scope="function")
def redefined_edges():
    return [("A", "B", 3), ("A", "B", 9)]


@fixture(scope="function")
def bidirectional_edges():
    return [("A", "B", 3), ("B", "A", 9)]


@fixture(scope="function")
def undefined_node_edges():
    return [("A", "B", 3), ("A", "C", 9)]


@fixture(scope="function")
def negative_edge_cost():
    return [("A", "B", 3), ("A", "C", -9)]


@fixture(scope="module")
def graph_test_set_1():
    yield Controller(
        devices=["A", "B", "C", "D"],
        connections=[("A", "B", 24), ("A", "C", 3), ("A", "D", 20), ("D", "C", 12)],
    )


@fixture(scope="module")
def graph_test_set_2():
    yield Controller(
        devices=["A", "B", "C", "D"],
        connections=[("A", "B", 24), ("A", "C", 3), ("A", "D", 20), ("C", "D", 12)],
    )
