import re
import json
import geojson
import pyproj
import shapely
from shapely import wkt
from shapely.geometry import shape
from shapely.ops import transform
from uuid import uuid4
from rdflib import URIRef, Literal, Namespace


def from_geojson_to_wkt(geojson_obj:dict):
    a = json.dumps(geojson_obj)
    geo = geojson.loads(a)
    geom = shape(geo)

    return geom.wkt

def merge_geojson_features_from_one_property(feature_collection, property_name:str):
    """
    Merge all features of a geojson object which have the same property (name for instance)
    """

    new_geojson_features = []
    features_to_merge = {}
    
    features_key = "features"
    crs_key = "crs"

    for feat in feature_collection.get(features_key):
        # Get property value for the feature
        property_value = feat.get("properties").get(property_name)

        # If the value is blank or does not exist, generate an uuid
        if property_value in [None, ""]:
            empty_value = True
            property_value = uuid4().hex
            feature_template = {"type":"Feature", "properties":{}}
        else:
            empty_value = False
            feature_template = {"type":"Feature", "properties":{property_name:property_value}}

        features_to_merge_key = features_to_merge.get(property_value)

        if features_to_merge_key is None:
            features_to_merge[property_value] = [feature_template, [feat]]
        else:
            features_to_merge[property_value][1].append(feat)

    for elem in features_to_merge.values():
        template, feature = elem

        geom_collection_list = []
        for portion in feature:
            geom_collection_list.append(portion.get("geometry"))
    
        geom_collection = {"type": "GeometryCollection", "geometries": geom_collection_list}
        template["geometry"] = geom_collection
        new_geojson_features.append(template)

    new_geojson = {"type":"FeatureCollection", features_key:new_geojson_features}

    crs_value = feature_collection.get(crs_key)
    if crs_value is not None :
        new_geojson[crs_key] = crs_value

    return new_geojson

def get_union_of_geosparql_wktliterals(wkt_literal_list:list[Literal]):
    GEO = Namespace("http://www.opengis.net/ont/geosparql#")
    geom_list = []
    for wkt_literal in wkt_literal_list:
        wkt_geom_value, wkt_geom_srid = get_wkt_geom_from_geosparql_wktliteral(wkt_literal)
        geom = wkt.loads(wkt_geom_value)
        geom_list.append(geom)

    geom_union = shapely.union_all(geom_list)
    geom_union_wkt = shapely.to_wkt(geom_union)
    wkt_literal_union = Literal(f"{wkt_geom_srid.n3()} {geom_union_wkt}", datatype=GEO.wktLiteral)

    return wkt_literal_union

def get_wkt_geom_from_geosparql_wktliteral(wktliteral:str):
    """
    Extraire le WKT et le l'URI SRID de la géométrie si elle est indiquée
    """

    wkt_srid_pattern = "<(.{0,})>"
    wkt_value_pattern = "<.{0,}> {1,}"
    wkt_geom_srid_match = re.match(wkt_srid_pattern, wktliteral)
    
    epsg_4326_uri = URIRef("http://www.opengis.net/def/crs/EPSG/0/4326")
    crs84_uri = URIRef("http://www.opengis.net/def/crs/OGC/1.3/CRS84")

    if wkt_geom_srid_match is not None:
        wkt_geom_srid = URIRef(wkt_geom_srid_match.group(1))
    else:
        wkt_geom_srid = epsg_4326_uri

    if wkt_geom_srid == crs84_uri:
        wkt_geom_srid = epsg_4326_uri
    wkt_geom_value = re.sub(wkt_value_pattern, "", wktliteral)

    return wkt_geom_value, wkt_geom_srid

def transform_geometry_crs(geom, crs_from, crs_to):
    """
    Obtenir une géométrie définie dans le système de coordonnées `from_crs` vers le système `to_crs`.
    """

    project = pyproj.Transformer.from_crs(crs_from, crs_to, always_xy=True).transform
    return transform(project, geom)

def get_pyproj_crs_from_opengis_epsg_uri(opengis_epsg_uri:URIRef):
    """
    Extraction du code EPSG à partir de `opengis_epsg_uri` pour renvoyer un objet pyproj.CRS
    """
    pattern = "http://www.opengis.net/def/crs/EPSG/0/([0-9]{1,})"
    try :
        epsg_code = re.match(pattern, opengis_epsg_uri.strip()).group(1)
        return pyproj.CRS(f'EPSG:{epsg_code}')
    except :
        return None

def are_similar_geometries(geom_1, geom_2, geom_type:str, coef_min:float=0.8, max_dist=10) -> bool:
    """
    La fonction détermine si deux géométries sont similaires
    `coef_min` est dans [0,1] et définit la valeur minimale pour considérer que `geom_1` et `geom_2` soient similaires
    `geom_type` définit le type de géométrie à prendre en compte (`point`, `linestring`, `polygon`)
    """
    # geom_intersection = geom_1.intersection(geom_2)
    # geom_union = geom_1.union(geom_2)
    # coef = geom_intersection.area/geom_union.area

    # if coef > 0.7:
    #     return True
    # else:
    #     return False

    if geom_type == "polygon":
        return are_similar_polygons(geom_1, geom_2, coef_min)
    elif geom_type == "point":
        return are_similar_points(geom_1, geom_2, max_dist)
    return None

    
def are_similar_points(geom_1, geom_2, max_dist):
    """
    On cherche à savoir si deux points sont similaires, ils le sont si la distance qui les sépare est inférieure à `max_dist`.
    """

    dist = geom_1.distance(geom_2)

    if dist <= max_dist:
        return True
    else:
        return False


def are_similar_polygons(geom_1, geom_2, coef_min:float):
    """
    Techinique pour savoir si les polygones sont similaires :
    * on construction une bounding bbox pour chaque polygone
    * on analyse le recouvrement de l'union des bbox et de l'intersection

    Si le taux de recouvrement est supérieur à `coef_min`, les polygones sont similaires
    """

    geom_intersection = geom_1.envelope.intersection(geom_2.envelope)
    geom_union = geom_1.envelope.union(geom_2.envelope)
    coef = geom_intersection.area/geom_union.area

    if coef >= coef_min:
        return True
    else:
        return False
    

def get_processed_geometry(geom_wkt:str, geom_srid_uri:URIRef, geom_type:str, crs_uri:URIRef, buffer_radius:float):
    """
    Obtention d'une géométrie pour pouvoir la comparer aux autres :
    * ses coordonnées seront exprimées dans le référentiel lié à `crs_uri`
    * si la géométrie est une ligne ou un point (area=0.0) et qu'on veut avoir un polygone comme géométrie (`geom_type == "polygon"`), alors on récupère une zone tampon dont le buffer est donné par `buffer_radius`
    """

    geom = wkt.loads(geom_wkt)
    crs_from = get_pyproj_crs_from_opengis_epsg_uri(geom_srid_uri)
    crs_to = get_pyproj_crs_from_opengis_epsg_uri(crs_uri)

    # Conversion de la géométrie vers le système de coordonnées cible
    if crs_from != crs_to:
        geom = transform_geometry_crs(geom, crs_from, crs_to)
    
    # Ajout d'un buffer `meter_buffer` mètres si c'est pas un polygone
    if geom.area == 0.0 and geom_type == "polygon":
        geom = geom.buffer(buffer_radius)

    return geom