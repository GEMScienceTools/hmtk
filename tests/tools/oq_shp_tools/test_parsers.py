"""
"""

import os
import unittest

from hmtk.tools.oq_shp_tools.parsers import parse_area_source_shp


class ParsersTestCase(unittest.TestCase):
    """
    """
    BASE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'dat')

    def setUp(self):
        """
        Fix the name of the sample shapefile

        """

        flnme = 'oq_area_source_template.shp'
        self.filename = os.path.join(self.BASE_DATA_PATH, flnme)

    def test_parse_area_source_shp(self):
        """
        This tests that the parameters in the shapefile attribute table are
        correct.
        """

        # Get the list of area sources included in the shapefile
        source_list = parse_area_source_shp(self.filename)

        # Check the parameters of the first source
        src = source_list[0]
        self.assertTrue(src.id == '1')
        self.assertTrue(src.name == 'Sample OQ area source')
        self.assertTrue(src.trt == 'Active Shallow Crust')
        self.assertTrue(src.mag_scale_rel == 'WC1994')
        self.assertTrue(src.rupt_aspect_ratio == 2.0)
        # Check mfd
        self.assertTrue(src.mfd.a_val == 3.001)
        self.assertTrue(src.mfd.b_val == 1.001)
        # Check nodal plane
        self.assertTrue(src.nodal_plane_dist[0].rake == 179.9)
        self.assertTrue(src.nodal_plane_dist[0].strike == 359.9)
        self.assertTrue(src.nodal_plane_dist[0].dip == 89.99)
        self.assertTrue(src.nodal_plane_dist[0].probability == 1.0)
        # Check nodal plane
        self.assertTrue(src.hypo_depth_dist[0].depth == 10.0)
        self.assertTrue(src.hypo_depth_dist[0].probability == 1.0)
        # Check nodal plane
        self.assertTrue(src.geometry.upper_seismo_depth == 0.0)
        self.assertTrue(src.geometry.lower_seismo_depth == 20.0)
