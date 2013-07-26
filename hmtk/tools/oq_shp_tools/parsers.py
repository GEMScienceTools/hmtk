"""
Module for parsing preformatted shapefiles containing information about
OQ-engine source typologies
"""

import ogr
import sys

from openquake.nrmllib.models import AreaSource, TGRMFD, NodalPlane, \
    HypocentralDepth, AreaGeometry


def _get_area_geometry(feature):
    """
    This function gets the geometry of a polygon feature

    :returns:
        An instance of the :class:`AreaGeometry` defined in the oq-nrmllib
        models.py module
    """
    geometry = feature.GetGeometryRef()
    pts = geometry.GetGeometryRef(0)
    points = []
    wkt_str = 'POLYGON(('
    for point in xrange(pts.GetPointCount()):
        points.append((pts.GetX(point), pts.GetY(point)))
        wkt_str += '%.5f %.5f,' % (pts.GetX(point), pts.GetY(point))
    wkt_str = '))'

    upp_seismo = feature.GetField('upp_seismo')
    low_seismo = feature.GetField('low_seismo')

    # Create the area geometry object
    area_geom = AreaGeometry(wkt=wkt_str, upper_seismo_depth=upp_seismo,
                             lower_seismo_depth=low_seismo)

    return area_geom


def _get_hypo_depth_distr(feature):
    """
    Get information about the hypocentral depth distribution contained in the
    shapefile attribute table for the current feature

    :returns:
        A list of :class:`HypocentralDepth` instances defined in the oq-nrmllib
        models.py module

    """

    nodal_plane_list = []
    num_npd = feature.GetField('num_npd')
    for i in range(0, num_npd):
        idx = i + 1
        depth = feature.GetField('hdd_d_%d' % (idx))
        prob = feature.GetField('hdd_w_%d' % (idx))
        nodal_plane_list.append(HypocentralDepth(probability=prob,
                                                 depth=depth))
    return nodal_plane_list


def _get_nodal_plane_distr(feature):
    """
    Get information about the nodal plane distribution contained in the
    shapefile attribute table for the current feature

    :returns:
        A list of :class:`NodalPlane` instances

    """

    nodal_plane_list = []
    num_npd = feature.GetField('num_npd')
    for i in range(0, num_npd):
        idx = i + 1
        strike = feature.GetField('strike_%d' % (idx))
        dip = feature.GetField('dip_%d' % (idx))
        rake = feature.GetField('rake_%d' % (idx))
        prob = feature.GetField('weight_%d' % (idx))

        nodal_plane_list.append(NodalPlane(probability=prob, strike=strike,
                                           dip=dip, rake=rake))
    return nodal_plane_list


def _get_truncGR_from_feature(feature):
    """
    Get fields from the attribute table and created a :class:`TGRMFD`
    instance

    :returns:
        A :class:`TGRMFD` instance

    """

    a_val = feature.GetField('a_value')
    b_val = feature.GetField('b_value')
    min_mag = feature.GetField('min_mag')
    max_mag = feature.GetField('max_mag')
    return TGRMFD(a_val=a_val, b_val=b_val, min_mag=min_mag, max_mag=max_mag)


def parse_area_source_shp(filename):
    """
    Parse an preformatted shapefile containing information about area
    sources

    :returns:
        A list of :class:`AreaSource` istances

    """

    driver = ogr.GetDriverByName('ESRI Shapefile')
    data_source = driver.Open(filename, 0)
    if data_source is None:
        print 'Could not open ' + filename
        sys.exit(1)

    layer = data_source.GetLayer()

    # number of features
    num_features = layer.GetFeatureCount()
    print 'Number of features:', num_features

    sourcelist = []
    feature = layer.GetNextFeature()
    while feature:

        src_id = feature.GetField('src_id')
        name = feature.GetField('src_name')
        tect_reg = feature.GetField('tect_reg')

        # Geometry parameters
        mag_scal = feature.GetField('mag_scal_r')
        rup_asp_ratio = feature.GetField('rup_asp_ra')

        # Computing the MFD distribution
        mfd_type = feature.GetField('mfd_type')
        if mfd_type == 'truncGutenbergRichterMFD':
            mfd = _get_truncGR_from_feature(feature)

        # Create the nodal plane distribution
        nodal_planes_list = _get_nodal_plane_distr(feature)

        # Create the hypocentral depth distribution
        hypo_depth_list = _get_hypo_depth_distr(feature)

        # Create the area source geometry
        geometry = _get_area_geometry(feature)

        # Append the AreaSource to the list of sources
        sourcelist.append(AreaSource(id=src_id,
                          name=name,
                          geometry=geometry,
                          trt=tect_reg,
                          mag_scale_rel=mag_scal,
                          rupt_aspect_ratio=rup_asp_ratio,
                          mfd=mfd,
                          nodal_plane_dist=nodal_planes_list,
                          hypo_depth_dist=hypo_depth_list))

        # Get the next feature
        feature = layer.GetNextFeature()

    return sourcelist
