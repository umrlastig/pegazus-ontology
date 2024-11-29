from namespaces import NameSpaces
import geomprocessing as gp
import strprocessing as sp
import graphdb as gd
import graphrdf as gr
from rdflib import URIRef, Graph

np = NameSpaces()

def compare_attribute_versions(graphdb_url:str, repository_name:str, comp_named_graph_name:str, comp_tmp_file:str, comparison_settings:dict={}):
    """
    Compare versions related to the same attribute. The way of versions are compared are set by `comparison_settings`.
    """

    # Get versions which have to be compared
    results = get_attribute_versions_to_compare(graphdb_url, repository_name)

    # Initialisation of a RDFLib graph (it will be exported as a TTL file at the end of the process)
    g = Graph() 

    # Dictionary which defines properties to used according comparison outputs.
    val_comp_dict = {True:np.ADDR["sameVersionValueAs"], False:np.ADDR["differentVersionValueFrom"], None:None}

    for elem in results.get("results").get("bindings"):
        # Get URIs (attribute and attribute versions)
        attr_type = gr.convert_result_elem_to_rdflib_elem(elem.get('attrType'))
        lm_type = gr.convert_result_elem_to_rdflib_elem(elem.get('ltype'))
        attr_vers_1 = gr.convert_result_elem_to_rdflib_elem(elem.get('attrVers1'))
        attr_vers_2 = gr.convert_result_elem_to_rdflib_elem(elem.get('attrVers2'))
        vers_val_1 = gr.convert_result_elem_to_rdflib_elem(elem.get('versVal1'))
        vers_val_2 = gr.convert_result_elem_to_rdflib_elem(elem.get('versVal2'))

        # If the attribute describes a name, comparison is done thanks to `are_similar_name_versions()`.
        # This comparison depends on the type of landmark (`lm_type`)
        if attr_type == np.ATYPE["Name"]:
            is_same_value = are_similar_name_versions(lm_type, vers_val_1, vers_val_2)
  
        # If the attribute describes a geometry, comparison is done thanks to `are_similar_geom_versions()`.
        # This comparison depends on the type of landmark (`lm_type`)
        elif attr_type == np.ATYPE["Geometry"]:
            similarity_coef = comparison_settings.get("geom_similarity_coef")
            buffer_radius = comparison_settings.get("geom_buffer_radius")
            crs_uri = comparison_settings.get("geom_crs_uri")
            is_same_value = are_similar_geom_versions(lm_type, vers_val_1, vers_val_2, similarity_coef, buffer_radius, crs_uri)
        else:
            is_same_value = None
        
        # Get the property to be used to compare versions according the result of comparison
        # Add the triple in the graph
        comp_pred = val_comp_dict.get(is_same_value)
        if comp_pred is not None:
            g.add((attr_vers_1, comp_pred, attr_vers_2))
    
    # Export the graph to of TTL file
    g.serialize(destination=comp_tmp_file)
    
    # Import the TTL file in GraphDB
    gd.import_ttl_file_in_graphdb(graphdb_url, repository_name, comp_tmp_file, named_graph_name=comp_named_graph_name)
        
def get_geom_type_according_landmark_type(rel_lm_type:URIRef):
    """
    According landmark type, return a shape of geometry.
    """
    
    if rel_lm_type in [np.LTYPE["HouseNumber"], np.LTYPE["StreetNumber"], np.LTYPE["DistrictNumber"]]:
        return "point"
    elif rel_lm_type in [np.LTYPE["Thoroughfare"], np.LTYPE["District"], np.LTYPE["Municipality"]]:
        return "polygon"
    else:
        return "polygon"

def get_name_type_according_landmark_type(rel_lm_type:URIRef):
    """
    According landmark type, return a value (housenumber, thoroughfare, area)
    """
    if rel_lm_type in [np.LTYPE["HouseNumber"], np.LTYPE["StreetNumber"], np.LTYPE["DistrictNumber"]]:
        return "housenumber"
    elif rel_lm_type in [np.LTYPE["Thoroughfare"]]:
        return "thoroughfare"
    elif rel_lm_type in [np.LTYPE["District"], np.LTYPE["Municipality"]]:
        return "area"
    else:
        return ""

def are_similar_geom_versions(lm_type, vers_val_1, vers_val_2, similarity_coef, buffer_radius, crs_uri) -> bool:
    """
    Returns True if `vers_val_1` is similar to `vers_val_2`, False else.
    Similarity depends on type of landmark (`lm_type`) and coefficient of similarity (`similarity_coef`).
    To comparable geometries, they must have the same shape (point, linestring, polygon) so buffer radius (`buffer_radius`) is used for linestring to be converted as polygon if needed.
    Besides, for geometries to have same coordinated reference system (`crs_uri`).
    """

    # Get the suitable shape type of geometries (point, linestring, polygon) to compare them according landmark type
    geom_type = get_geom_type_according_landmark_type(lm_type)

    # Extract wkt literal and cri uri from vers_val Literal and modify wkt literal if needed (add buffer and change CRS)
    geom_wkt_1, geom_srid_uri_1 = gp.get_wkt_geom_from_geosparql_wktliteral(vers_val_1.strip())
    geom_1 = gp.get_processed_geometry(geom_wkt_1, geom_srid_uri_1, geom_type, crs_uri, buffer_radius)
    geom_wkt_2, geom_srid_uri_2 = gp.get_wkt_geom_from_geosparql_wktliteral(vers_val_2.strip())
    geom_2 = gp.get_processed_geometry(geom_wkt_2, geom_srid_uri_2, geom_type, crs_uri, buffer_radius)

    return gp.are_similar_geometries(geom_1, geom_2, geom_type, similarity_coef, max_dist=buffer_radius)

def are_similar_name_versions(lm_type, vers_val_1, vers_val_2):
    name_type = get_name_type_according_landmark_type(lm_type)
    normalized_name_1, simplified_name_1 = sp.normalize_and_simplify_name_version(vers_val_1.strip(), name_type, name_lang=vers_val_1.language)
    normalized_name_2, simplified_name_2 = sp.normalize_and_simplify_name_version(vers_val_2.strip(), name_type, name_lang=vers_val_2.language)

    if simplified_name_1 == simplified_name_2:
        return True
    else:
        return False

def get_attribute_versions_to_compare(graphdb_url:str, repository_name:str):
    query = np.query_prefixes  + f"""
        SELECT DISTINCT ?ltype ?attrType ?attrVers1 ?attrVers2 ?versVal1 ?versVal2 WHERE {{
            ?rootLm a addr:Landmark ; addr:isRootOf ?lm1, ?lm2.
            ?lm1 addr:hasAttribute [addr:isAttributeType ?attrType ; addr:hasAttributeVersion ?attrVers1] ; addr:isLandmarkType ?ltype .
            ?lm2 addr:hasAttribute [addr:isAttributeType ?attrType ; addr:hasAttributeVersion ?attrVers2] .
            ?attrVers1 addr:versionValue ?versVal1 .
            ?attrVers2 addr:versionValue ?versVal2 .
            FILTER(!sameTerm(?lm1, ?lm2))
            MINUS {{
                ?attrVers1 ?p ?attrVers2 .
                FILTER(?p IN (addr:sameVersionValueAs, addr:differentVersionValueFrom))
            }}
        }}
    """

    results = gd.select_query_to_json(query, graphdb_url, repository_name)

    return results