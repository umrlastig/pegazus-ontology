from namespaces import NameSpaces
import geomprocessing as gp
import strprocessing as sp
import graphdb as gd
import graphrdf as gr
from rdflib import URIRef, Graph

np = NameSpaces()

def compare_attribute_versions(graphdb_url:str, repository_name:str, comp_named_graph_name:str, comp_tmp_file:str, comparison_settings:dict={}):
    results = get_attribute_versions_to_compare(graphdb_url, repository_name)
    g = Graph()
    val_comp_dict = {True:np.ADDR["sameVersionValueAs"], False:np.ADDR["differentVersionValueFrom"], None:None}

    for elem in results.get("results").get("bindings"):
        # Récupération des URIs (attibut et version d'attribut)
        attr_type = gr.convert_result_elem_to_rdflib_elem(elem.get('attrType'))
        lm_type = gr.convert_result_elem_to_rdflib_elem(elem.get('ltype'))
        attr_vers_1 = gr.convert_result_elem_to_rdflib_elem(elem.get('attrVers1'))
        attr_vers_2 = gr.convert_result_elem_to_rdflib_elem(elem.get('attrVers2'))
        vers_val_1 = gr.convert_result_elem_to_rdflib_elem(elem.get('versVal1'))
        vers_val_2 = gr.convert_result_elem_to_rdflib_elem(elem.get('versVal2'))

        if attr_type == np.ATYPE["Name"]:
            is_same_value = are_similar_name_versions(lm_type, vers_val_1, vers_val_2)
  
        elif attr_type == np.ATYPE["Geometry"]:
            similarity_coef = comparison_settings.get("geom_similarity_coef")
            buffer_radius = comparison_settings.get("geom_buffer_radius")
            crs_uri = comparison_settings.get("geom_crs_uri")
            is_same_value = are_similar_geom_versions(lm_type, vers_val_1, vers_val_2, similarity_coef, buffer_radius, crs_uri)
        else:
            is_same_value = None
        
        comp_pred = val_comp_dict.get(is_same_value)
        if comp_pred is not None:
            g.add((attr_vers_1, comp_pred, attr_vers_2))
    
    g.serialize(destination=comp_tmp_file)
    gd.import_ttl_file_in_graphdb(graphdb_url, repository_name, comp_tmp_file, named_graph_name=comp_named_graph_name)
        
def get_geom_type_according_landmark_type(rel_lm_type:URIRef):
    if rel_lm_type in [np.LTYPE["HouseNumber"], np.LTYPE["StreetNumber"], np.LTYPE["DistrictNumber"]]:
        return "point"
    elif rel_lm_type in [np.LTYPE["Thoroughfare"], np.LTYPE["District"], np.LTYPE["Municipality"]]:
        return "polygon"
    else:
        return "polygon"

def get_name_type_according_landmark_type(rel_lm_type:URIRef):
    if rel_lm_type in [np.LTYPE["HouseNumber"], np.LTYPE["StreetNumber"], np.LTYPE["DistrictNumber"]]:
        return "housenumber"
    elif rel_lm_type in [np.LTYPE["Thoroughfare"]]:
        return "thoroughfare"
    elif rel_lm_type in [np.LTYPE["District"], np.LTYPE["Municipality"]]:
        return "area"
    else:
        return ""

def are_similar_geom_versions(lm_type, vers_val_1, vers_val_2, similarity_coef, buffer_radius, crs_uri):
    geom_type = get_geom_type_according_landmark_type(lm_type)
    geom_wkt_1, geom_srid_uri_1 = gp.get_wkt_geom_from_geosparql_wktliteral(vers_val_1.strip())
    geom_1 = gp.get_processed_geometry(geom_wkt_1, geom_srid_uri_1, geom_type, crs_uri, buffer_radius)
    geom_wkt_2, geom_srid_uri_2 = gp.get_wkt_geom_from_geosparql_wktliteral(vers_val_2.strip())
    geom_2 = gp.get_processed_geometry(geom_wkt_2, geom_srid_uri_2, geom_type, crs_uri, buffer_radius)

    return gp.are_similar_geometries(geom_1, geom_2, geom_type, similarity_coef, max_dist=buffer_radius)

def are_similar_name_versions(lm_type, vers_val_1, vers_val_2):
    name_type = get_name_type_according_landmark_type(lm_type)
    normalized_name_1, simplified_name_1 = sp.normalize_and_simplify_name_version(vers_val_1.strip(), name_type, name_lang=vers_val_1.language)
    normalized_name_2, simplified_name_2 = sp.normalize_and_simplify_name_version(vers_val_2.strip(), name_type, name_lang=vers_val_2.language)

    if simplified_name_1 == simplified_name_1:
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