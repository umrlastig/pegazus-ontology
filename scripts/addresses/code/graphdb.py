import os
import filemanagement as fm
import curl as curl
import urllib.parse as up
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.namespace import RDF
import json

def get_repository_uri_from_name(graphdb_url, repository_name):
    return URIRef(f"{graphdb_url}/repositories/{repository_name}")

def get_named_graph_uri_from_name(graphdb_url, repository_name, named_graph_name):
    return URIRef(f"{graphdb_url}/repositories/{repository_name}/rdf-graphs/{named_graph_name}")

def get_repository_uri_statements_from_name(graphdb_url, repository_name):
    return URIRef(f"{graphdb_url}/repositories/{repository_name}/statements")

def remove_named_graph(graphdb_url, repository_name, named_graph_name):
    cmd = curl.get_curl_command("DELETE", get_named_graph_uri_from_name(graphdb_url, repository_name, named_graph_name).strip())
    os.system(cmd)

def remove_named_graph_from_uri(named_graph_uri:URIRef):
    cmd = curl.get_curl_command("DELETE", named_graph_uri.strip())
    os.system(cmd)

def remove_named_graphs(graphdb_url,repository_name,named_graph_name_list):
    for g in named_graph_name_list:
        remove_named_graph(graphdb_url, repository_name, g)

def remove_named_graphs_from_uris(named_graph_uris_list):
    for g in named_graph_uris_list:
        remove_named_graph_from_uri(g)

def remove_named_graph_from_query(graphdb_url, repository_name, named_graph_name):
    graph_uri = get_named_graph_uri_from_name(graphdb_url, repository_name, named_graph_name)

    query = f"""
    DELETE {{
        GRAPH ?g {{
            ?s ?p ?o
        }}
    }}
    WHERE {{
        BIND ({graph_uri.n3()} AS ?g)
        GRAPH ?g {{
            ?s ?p ?o
        }}
    }}
    """
    
    update_query(query, graphdb_url, repository_name)

def remove_named_graphs_from_query(graphdb_url, repository_name, named_graph_names_list):
    named_graph_uris_list = []
    selected_named_graphs = ""
    for named_graph_name in named_graph_names_list:
        named_graph_uris_list.append(get_named_graph_uri_from_name(graphdb_url, repository_name, named_graph_name).n3())

    selected_named_graphs = ",".join(named_graph_uris_list)

    query = f"""
    DELETE {{
        GRAPH ?g {{
            ?s ?p ?o
        }}
    }}
    WHERE {{
        GRAPH ?g {{
            ?s ?p ?o
        }}
        FILTER (?g in ({selected_named_graphs}))
    }}
    """

    update_query(query, graphdb_url, repository_name)

def create_config_local_repository_file(config_repository_file:str, repository_name:str, ruleset_name:str="rdfsplus-optimized", disable_same_as:bool=True, check_for_inconsistencies:bool=False):
    rep = Namespace("http://www.openrdf.org/config/repository#")
    sr = Namespace("http://www.openrdf.org/config/repository/sail#")
    sail = Namespace("http://www.openrdf.org/config/sail#")
    graph_db = Namespace("http://www.ontotext.com/config/graphdb#")
    g = Graph()

    elem = BNode()
    repository_impl = BNode()
    sail_impl = BNode()
    
    disable_same_as_str = str(disable_same_as).lower()

    # ruleset_name can be the name of built-in ruleset ("owl-max", rdfsplus-optimized"...) of the path of a ruleset file
    if ruleset_name is None:
        ruleset_name = "empty"
        
    g.add((elem, RDF.type, rep.Repository))
    g.add((elem, rep.repositoryID, Literal(repository_name)))
    g.add((elem, rep.repositoryImpl, repository_impl))
    g.add((repository_impl, rep.repositoryType, Literal("graphdb:SailRepository")))
    g.add((repository_impl, sr.sailImpl, sail_impl))
    g.add((sail_impl, sail.sailType, Literal("graphdb:Sail")))
    g.add((sail_impl, graph_db["base-URL"], Literal("http://example.org/owlim#")))
    g.add((sail_impl, graph_db["defaultNS"], Literal("")))
    g.add((sail_impl, graph_db["entity-index-size"], Literal("10000000")))
    g.add((sail_impl, graph_db["entity-id-size"], Literal("32")))
    g.add((sail_impl, graph_db["imports"], Literal("")))
    g.add((sail_impl, graph_db["repository-type"], Literal("file-repository")))
    g.add((sail_impl, graph_db["ruleset"], Literal(ruleset_name)))
    g.add((sail_impl, graph_db["storage-folder"], Literal("storage")))
    g.add((sail_impl, graph_db["enable-context-index"], Literal("false")))
    g.add((sail_impl, graph_db["enablePredicateList"], Literal("true")))
    g.add((sail_impl, graph_db["in-memory-literal-properties"], Literal("true")))
    g.add((sail_impl, graph_db["enable-literal-index"], Literal("true")))
    g.add((sail_impl, graph_db["check-for-inconsistencies"], Literal(check_for_inconsistencies)))
    g.add((sail_impl, graph_db["disable-sameAs"], Literal(disable_same_as_str)))
    g.add((sail_impl, graph_db["query-timeout"], Literal("0")))
    g.add((sail_impl, graph_db["query-limit-results"], Literal("0")))
    g.add((sail_impl, graph_db["throw-QueryEvaluationException-on-timeout"], Literal("false")))
    g.add((sail_impl, graph_db["read-only"], Literal("false")))
    
    g.serialize(destination=config_repository_file)

def reinfer_repository(graphdb_url, repository_name):
    """
    According to GraphDB : 'Statements are inferred only when you insert new statements. So, if reconnected to a repository with a different ruleset, it does not take effect immediately.'
    This function reinfers repository
    """
    
    query = """
    prefix sys: <http://www.ontotext.com/owlim/system#>
    INSERT DATA { [] sys:reinfer [] }
    """

    update_query(query, graphdb_url, repository_name)

def turn_inference_off(graphdb_url, repository_name):
    query = """
    prefix sys: <http://www.ontotext.com/owlim/system#>
    INSERT DATA { [] sys:turnInferenceOff [] }
    """

    update_query(query, graphdb_url, repository_name)


def turn_inference_on(graphdb_url, repository_name):
    query = """
    prefix sys: <http://www.ontotext.com/owlim/system#>
    INSERT DATA { [] sys:turnInferenceOn [] }
    """

    update_query(query, graphdb_url, repository_name)

def add_ruleset_from_file(graphdb_url, repository_name, ruleset_file, ruleset_name):
    query  = f"""
    prefix sys: <http://www.ontotext.com/owlim/system#>
    INSERT DATA {{
        <_:{ruleset_name}> sys:addRuleset <file:{ruleset_file}>
    }}
    """

    update_query(query, graphdb_url, repository_name)

def add_ruleset_from_name(graphdb_url, repository_name, ruleset_name):
    query  = f"""
    prefix sys: <http://www.ontotext.com/owlim/system#>
    INSERT DATA {{
        _:b sys:addRuleset "{ruleset_name}"
    }}
    """

    update_query(query, graphdb_url, repository_name)

def change_ruleset(graphdb_url, repository_name, ruleset_name):
    query = f"""
    prefix sys: <http://www.ontotext.com/owlim/system#>
    INSERT DATA {{
        _:b sys:defaultRuleset "{ruleset_name}"
    }}
    """

    update_query(query, graphdb_url, repository_name)

def create_repository_from_config_file(graphdb_url:str, local_config_file:str):
    url = f"{graphdb_url}/rest/repositories"
    curl_cmd_local = curl.get_curl_command("POST", url, content_type="multipart/form-data", form=f"config=@{local_config_file}")
    os.system(curl_cmd_local)

def export_data_from_repository(graphdb_url, repository_name, out_ttl_file, named_graph_name:str=None, named_graph_uri:URIRef=None):
    if named_graph_uri is not None:
        pass
    elif named_graph_name is not None:
        named_graph_uri = get_named_graph_uri_from_name(graphdb_url, repository_name, named_graph_name)
    
    query_param = ""
    if named_graph_uri is not None:
        encoded_named_graph_uri = up.quote(named_graph_uri.n3())
        query_param += f"?context={encoded_named_graph_uri}"

    url = get_repository_uri_statements_from_name(graphdb_url, repository_name).strip() + query_param
    cmd = curl.get_curl_command("GET", url, content_type="application/x-www-form-urlencoded", accept="text/turtle")

    out_content = os.popen(cmd)
    fm.write_file(out_content.read(), out_ttl_file)

def select_query_to_txt_file(query, graphdb_url, repository_name, res_query_file):
    query_encoded = up.quote(query)
    post_data = f"query={query_encoded}"
    str_uri = get_repository_uri_from_name(graphdb_url, repository_name).strip()
    cmd = curl.get_curl_command("POST", str_uri, content_type="application/x-www-form-urlencoded", post_data=post_data)
    out_content = os.popen(cmd)
    fm.write_file(out_content.read(), res_query_file)

def select_query_to_json(query, graphdb_url, repository_name):
    query_encoded = up.quote(query)
    post_data = f"query={query_encoded}"
    str_uri = get_repository_uri_from_name(graphdb_url, repository_name).strip()
    cmd = curl.get_curl_command("POST", str_uri, content_type="application/x-www-form-urlencoded", accept="application/json", post_data=post_data)
    out_content = os.popen(cmd)
    return json.loads(out_content.read())

def construct_query_to_ttl(query, graphdb_url, repository_name, res_query_file):
    query_encoded = up.quote(query)
    post_data = f"query={query_encoded}"
    str_uri = get_repository_uri_from_name(graphdb_url, repository_name).strip()
    cmd = curl.get_curl_command("POST", str_uri, content_type="application/x-www-form-urlencoded", accept="text/turtle", post_data=post_data)
    out_content = os.popen(cmd)
    fm.write_file(out_content.read(), res_query_file)
    
def update_query(query, graphdb_url, repository_name):
    url = get_repository_uri_statements_from_name(graphdb_url, repository_name)
    query_encoded = up.quote(query)
    cmd = curl.get_curl_command("POST", url, content_type="application/x-www-form-urlencoded", post_data=f"update={query_encoded}")
    os.system(cmd)

def get_repository_namespaces(graphdb_url, repository_name):
    namespaces_uri = get_repository_uri_from_name(graphdb_url, repository_name).strip() + "/namespaces"
    cmd = curl.get_curl_command("GET", namespaces_uri.n3())
    namespaces_list = os.popen(cmd).read().split("\n")[1:]
    namespaces = {}

    for namespace in namespaces_list:
        try:
            prefix, uri = namespace.split(",")
            namespaces[prefix] = uri
        except ValueError:
            pass

    return namespaces

def add_prefix_to_repository(graphdb_url, repository_name, namespace:Namespace, prefix:str):
    url = get_repository_uri_from_name(graphdb_url, repository_name).strip() + "/namespaces/" + prefix
    cmd = curl.get_curl_command("PUT", url, content_type="text/plain", post_data=namespace.strip())
    os.system(cmd)

def add_prefixes_to_repository(graphdb_url, repository_name, namespace_prefixes:dict):
    for prefix, namespace in namespace_prefixes.items():
        add_prefix_to_repository(graphdb_url, repository_name, namespace, prefix)

def get_repository_prefixes(graphdb_url, repository_name, perso_namespaces:dict=None):
    """
    perso_namespaces is a dictionnary which stores personalised namespaces to add of overwrite repository namespaces.
    keys are prefixes and values are URIs
    Ex: `{"geo":Namespace("http://data.ign.fr/def/geofla")}`
    """

    namespaces = get_repository_namespaces(graphdb_url, repository_name)
    if perso_namespaces is not None:
        namespaces.update(perso_namespaces)

    prefixes = ""
    for prefix, uri in namespaces.items():
        str_uri = uri[""].n3()
        prefixes += f"PREFIX {prefix}: {str_uri}\n"
        
    return prefixes

def get_query_prefixes_from_namespaces(namespaces:dict):
    """
    `namespaces` is a dictionnary which stores personalised namespaces
    keys are prefixes and values are URIs
    Ex: `{"geo":Namespace("http://data.ign.fr/def/geofla")}`
    """

    prefixes = ""
    for prefix, uri in namespaces.items():
        str_uri = uri[""].n3()
        prefixes += f"PREFIX {prefix}: {str_uri}\n"
        
    return prefixes

### Import created ttl file in GraphDB
def import_ttl_file_in_graphdb(graphdb_url, repository_id, ttl_file, named_graph_name=None, named_graph_uri=None):
    # cmd = f"curl -X POST -H \"Content-Type:application/x-turtle\" -T \"{ttl_file}\" {graphdb_url}/repositories/{repository_id}/statements"
    if named_graph_uri is not None:
        url = named_graph_uri
    elif named_graph_name is not None:
        url = get_named_graph_uri_from_name(graphdb_url, repository_id, named_graph_name)
    else:
        url = get_repository_uri_statements_from_name(graphdb_url, repository_id)
    
    cmd = curl.get_curl_command("POST", url.strip(), content_type="application/x-turtle", local_file=ttl_file)
    msg = os.popen(cmd)
    return msg.read()

def clear_named_graph_of_repository(graphdb_url, repository_name, named_graph_uri:URIRef):
    """
    Remove all contents from repository
    The repository still exists
    """
    encoded_named_graph_uri = up.quote(named_graph_uri.n3())
    url = f"{graphdb_url}/repositories/{repository_name}/statements?context={encoded_named_graph_uri}"
    cmd = curl.get_curl_command("DELETE", url)
    os.system(cmd)

def clear_repository(graphdb_url, repository_name):
    """
    Remove all contents from repository
    The repository still exists
    """
    url = f"{graphdb_url}/repositories/{repository_name}/statements"
    cmd = curl.get_curl_command("DELETE", url, content_type="application/x-turtle")
    os.system(cmd)

def get_repository_existence(graphdb_url, repository_name):
    """
    Get a boolean to know if the repository already exists (True if yes, False else)
    """

    url = f"{graphdb_url}/rest/repositories/{repository_name}"
    cmd = curl.get_curl_command("GET", url, content_type="application/x-turtle")
    out_content = os.popen(cmd).read()

    if out_content == "":
        return False
    else:
        return True

def remove_repository(graphdb_url, repository_name):
    """
    Remove a repository defined by its name
    """
    url = f"{graphdb_url}/repositories/{repository_name}"
    cmd = curl.get_curl_command("DELETE", url, content_type="application/x-turtle")
    os.system(cmd)

def reinitialize_repository(graphdb_url, repository_name, repository_config_file, ruleset_file:str=None, ruleset_name:str=None, disable_same_as:bool=False, check_for_inconsistencies:bool=False, allow_removal:bool=True):
    """
    Reinitialize a repository by removing it and recreating it again
    """

    # This action is done only if the repository already exists
    if get_repository_existence(graphdb_url, repository_name):
        # Remove the repository
        # `allow_removal` is an option as, sometimes, removing a repository does not work
        # Else, just clear the repository
        if allow_removal:
            remove_repository(graphdb_url, repository_name)
        else:
            clear_repository(graphdb_url, repository_name)

    create_repository(graphdb_url, repository_name, repository_config_file, ruleset_file, ruleset_name, disable_same_as, check_for_inconsistencies)

def create_repository(graphdb_url, repository_name, repository_config_file, ruleset_file:str=None, ruleset_name:str=None, disable_same_as:bool=False, check_for_inconsistencies:bool=False):
    # Create a configuration file for the repository
    # Here `ruleset_name` is None as ruleset will be defined after having created the repository
    create_config_local_repository_file(repository_config_file, repository_name, ruleset_name=None, disable_same_as=disable_same_as, check_for_inconsistencies=check_for_inconsistencies)
    
    # Thanks to configuration file, create the repository
    create_repository_from_config_file(graphdb_url, repository_config_file)

    if ruleset_file is not None:
        ruleset_name = "perso_rules"
        add_ruleset_from_file(graphdb_url, repository_name, ruleset_file, ruleset_name)
    elif ruleset_name is not None:
        add_ruleset_from_name(graphdb_url, repository_name, ruleset_name)

    change_ruleset(graphdb_url, repository_name, ruleset_name)
    
def load_ontologies(graphdb_url, repository_name, ont_files:list[str]=[], ontology_named_graph_name="ontology"):
    ### Import all ontologies in a named graph in the given repository
    for ont_file in ont_files:
        import_ttl_file_in_graphdb(graphdb_url, repository_name, ont_file, ontology_named_graph_name)

def export_named_graph_and_reload_repository(graphdb_url, repository_name, ttl_file, named_graph_name, ont_file, ontology_named_graph_name):
    """
    Export a specified named graph a of a repository before removing it and reload the repository

    3 steps :
    * export named graph in TTL file
    * remove all triples of the repository (explicits and implicits)
    * re-import ontology and newly exported files

    :TODO: see if it is possible to remove easily implicit triples to avoid calling this function.
    """

    # Get the uri of the named graph according repository name and its name
    named_graph_uri = get_named_graph_uri_from_name(graphdb_url, repository_name, named_graph_name)

    # Export named graph in TTL file
    export_data_from_repository(graphdb_url, repository_name, ttl_file, named_graph_uri=named_graph_uri)

    # Reset the directory and fill it again with the ontology and the fact graph
    clear_repository(graphdb_url, repository_name)
    load_ontologies(graphdb_url, repository_name, [ont_file], ontology_named_graph_name)
    import_ttl_file_in_graphdb(graphdb_url, repository_name, ttl_file, named_graph_name)

def remove_all_same_as_triples(graphdb_url, repository_name):
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    DELETE {?s owl:sameAs ?o} WHERE {?s owl:sameAs ?o}
    """
    
    update_query(query, graphdb_url, repository_name)