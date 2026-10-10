import unittest
from unittest.mock import patch

import compose_diagrams.diagram as diagram_mod
from compose_diagrams.diagram import Diagram
from compose_diagrams.service import Service


class FakeVolume:
    built = []

    def __init__(self, name):
        self.name = name
        FakeVolume.built.append(name)

    def __rshift__(self, other):
        return self

    def __lshift__(self, other):
        return self


class FakeEdge:
    def __init__(self, *args, **kwargs):
        pass


def make_diagram():
    mysql = Service("mysql", "mysql", None, ["db-data"], [], [])
    postgres = Service("postgres", "postgres", None, ["db-data"], [], [])
    mysql.node, postgres.node = object(), object()
    return Diagram("t", [mysql, postgres], {"db-data": {}}, {}, name="t")


class SharedVolumeTests(unittest.TestCase):
    def test_shared_volume_drawn_once(self):
        FakeVolume.built = []
        with patch.object(diagram_mod, "Volume", FakeVolume), patch.object(
            diagram_mod, "Edge", FakeEdge
        ):
            dac = make_diagram().design_volumes()
        self.assertEqual(sorted(FakeVolume.built), ["db-data"])
        self.assertEqual(dac.count('Volume("db-data")'), 1)

    def test_each_service_links_to_the_shared_node(self):
        FakeVolume.built = []
        with patch.object(diagram_mod, "Volume", FakeVolume), patch.object(
            diagram_mod, "Edge", FakeEdge
        ):
            dac = make_diagram().design_volumes()
        self.assertIn("mysql", dac)
        self.assertIn("postgres", dac)
        self.assertEqual(dac.count("vol_db_data >>"), 2)

    def test_distinct_volumes_keep_their_own_nodes(self):
        FakeVolume.built = []
        web = Service("web", "web", None, ["vol-a"], [], [])
        api = Service("api", "api", None, ["vol-b"], [], [])
        web.node, api.node = object(), object()
        diagram = Diagram("t", [web, api], {"vol-a": {}, "vol-b": {}}, {}, name="t")
        with patch.object(diagram_mod, "Volume", FakeVolume), patch.object(
            diagram_mod, "Edge", FakeEdge
        ):
            dac = diagram.design_volumes()
        self.assertEqual(sorted(FakeVolume.built), ["vol-a", "vol-b"])
        self.assertIn('vol_vol_a = Volume("vol-a")', dac)
        self.assertIn('vol_vol_b = Volume("vol-b")', dac)


if __name__ == "__main__":
    unittest.main()
