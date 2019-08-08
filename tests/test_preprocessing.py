import unittest

from wme.vekg_helper import *


class TestVEkg(unittest.TestCase):

    # def setUp(self):

    # def tearDown(self):

    def test_load_graph_from_tuples_return_correct_nodes_data(self):
        graph_tuples_dict = {
            'nodes': (
                ('1', {'id': '1', 'attributes': {}, 'label': 'car 1', 'confidence': 0.1, 'processor': 'CarDetection'}),
                ('2', {'id': '2', 'attributes': {}, 'label': 'car 2', 'confidence': 0.2, 'processor': 'CarDetection'}),
            ),
            'edges': (
                ('1', '2', {'label': 'node1_node2', 'relations': {'distance': 1.2, 'isCrashing': 0.6}}),
            ),
        }

        expected_graph_nodes = {
            '1': {'attributes': {}, 'confidence': 0.1, 'id': '1', 'label': 'car 1', 'processor': 'CarDetection'},
            '2': {'attributes': {}, 'confidence': 0.2, 'id': '2', 'label': 'car 2', 'processor': 'CarDetection'}
        }

        graph = load_graph_from_tuples_dict(graph_tuples_dict)
        nodes_dict = dict(graph.nodes(data=True))
        self.assertDictEqual(nodes_dict, expected_graph_nodes)

    def test_load_graph_from_tuples_return_correct_edges_data(self):
        graph_tuples_dict = {
            'nodes': (
                ('1', {'id': '1', 'attributes': {}, 'label': 'car 1', 'confidence': 0.1, 'processor': 'CarDetection'}),
                ('2', {'id': '2', 'attributes': {}, 'label': 'car 2', 'confidence': 0.2, 'processor': 'CarDetection'}),
            ),
            'edges': (
                ('1', '2', {'label': 'node1_node2', 'relations': {'distance': 1.2, 'isCrashing': 0.6}}),
            ),
        }

        expected_graph_edges = [
            ('1', '2', {'label': 'node1_node2', 'relations': {'distance': 1.2, 'isCrashing': 0.6}})
        ]

        graph = load_graph_from_tuples_dict(graph_tuples_dict)
        edges_list = list(graph.edges(data=True))
        self.assertListEqual(edges_list, expected_graph_edges)
