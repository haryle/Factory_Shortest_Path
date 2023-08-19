import pytest

from src.shortest_path import INF, NULL, Controller


def test_controller_self_loop_edges(graph_nodes, self_loop_edges):
    with pytest.raises(Exception):
        Controller(
            devices=graph_nodes,
            connections=self_loop_edges,
        )


def test_controller_redefined_edges(graph_nodes, redefined_edges):
    with pytest.raises(Exception):
        Controller(
            devices=graph_nodes,
            connections=redefined_edges,
        )


def test_controller_bidirectional_edges(graph_nodes, bidirectional_edges):
    with pytest.raises(Exception):
        Controller(
            devices=graph_nodes,
            connections=bidirectional_edges,
        )


def test_controller_negative_cost(graph_nodes, negative_edge_cost):
    with pytest.raises(Exception):
        Controller(
            devices=graph_nodes,
            connections=negative_edge_cost,
        )


def test_nodes_auto_added(graph_nodes, undefined_node_edges):
    controller = Controller(
        devices=graph_nodes,
        connections=undefined_node_edges,
    )
    assert set(graph_nodes) != set(controller.Devices)


def test_SP_set_1_from_1(graph_test_set_1: Controller):
    output = graph_test_set_1.get_best_path_from_source("A")
    exp_dist = {"A": 0, "B": 24, "C": 3, "D": 20}
    exp_prev = {"A": NULL, "B": "A", "C": "A", "D": "A"}
    assert output[0] == exp_dist
    assert output[1] == exp_prev


def test_SP_set_1_from_2(graph_test_set_1: Controller):
    output = graph_test_set_1.get_best_path_from_source("B")
    exp_dist = {"A": INF, "B": 0, "C": INF, "D": INF}
    exp_prev = {"A": NULL, "B": NULL, "C": NULL, "D": NULL}
    assert output[0] == exp_dist
    assert output[1] == exp_prev


def test_SP_set_1_from_3(graph_test_set_1: Controller):
    output = graph_test_set_1.get_best_path_from_source("C")
    exp_dist = {"A": INF, "B": INF, "C": 0, "D": INF}
    exp_prev = {"A": NULL, "B": NULL, "C": NULL, "D": NULL}
    assert output[0] == exp_dist
    assert output[1] == exp_prev


def test_SP_set_1_from_4(graph_test_set_1: Controller):
    output = graph_test_set_1.get_best_path_from_source("D")
    exp_dist = {"A": INF, "B": INF, "C": 12, "D": 0}
    exp_prev = {"A": NULL, "B": NULL, "C": "D", "D": NULL}
    assert output[0] == exp_dist
    assert output[1] == exp_prev


def test_SP_set_2_from_1(graph_test_set_2: Controller):
    output = graph_test_set_2.get_best_path_from_source("A")
    exp_dist = {"A": 0, "B": 24, "C": 3, "D": 15}
    exp_prev = {"A": NULL, "B": "A", "C": "A", "D": "C"}
    assert output[0] == exp_dist
    assert output[1] == exp_prev


def test_SP_set_2_from_2(graph_test_set_2: Controller):
    output = graph_test_set_2.get_best_path_from_source("B")
    exp_dist = {"A": INF, "B": 0, "C": INF, "D": INF}
    exp_prev = {"A": NULL, "B": NULL, "C": NULL, "D": NULL}
    assert output[0] == exp_dist
    assert output[1] == exp_prev


def test_SP_set_2_from_3(graph_test_set_2: Controller):
    output = graph_test_set_2.get_best_path_from_source("C")
    exp_dist = {"A": INF, "B": INF, "C": 0, "D": 12}
    exp_prev = {"A": NULL, "B": NULL, "C": NULL, "D": "C"}
    assert output[0] == exp_dist
    assert output[1] == exp_prev


def test_SP_set_2_from_4(graph_test_set_2: Controller):
    output = graph_test_set_2.get_best_path_from_source("D")
    exp_dist = {"A": INF, "B": INF, "C": INF, "D": 0}
    exp_prev = {"A": NULL, "B": NULL, "C": NULL, "D": NULL}
    assert output[0] == exp_dist
    assert output[1] == exp_prev
