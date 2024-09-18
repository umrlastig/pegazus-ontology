import os
from rdflib import Graph, Namespace, Literal, URIRef, XSD, SKOS
from namespaces import NameSpaces
import strprocessing as sp
import geomprocessing as gp
import timeprocessing as tp
import graphdb as gd
import graphrdf as gr
import curl as curl

np = NameSpaces()

def add_alt_and_hidden_labels_to_landmarks(graphdb_url, repository_name, named_graph_uri:URIRef):
    add_alt_and_hidden_labels_for_name_attribute_versions(graphdb_url, repository_name, named_graph_uri)
    add_alt_and_hidden_labels_to_landmarks_from_name_attribute_versions(graphdb_url, repository_name, named_graph_uri)

def add_alt_and_hidden_labels_for_name_attribute_versions(graphdb_url, repository_name, factoids_named_graph_uri:URIRef):
    query = np.query_prefixes + f"""
        SELECT ?av ?name ?ltype WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
            GRAPH ?g {{ ?av a addr:AttributeVersion . }}
            ?av addr:versionValue ?name ;
                addr:isAttributeVersionOf [
                    a addr:Attribute ;
                    addr:isAttributeType atype:Name ;
                    addr:isAttributeOf [a addr:Landmark ; addr:isLandmarkType ?ltype]] .
        }}
        """

    results = gd.select_query_to_json(query, graphdb_url, repository_name)

    query_lines = ""
    for elem in results.get("results").get("bindings"):
        # Retrieval of URIs (attribute and attribute version) and geometry
        rel_av = gr.convert_result_elem_to_rdflib_elem(elem.get('av'))
        rel_name = gr.convert_result_elem_to_rdflib_elem(elem.get('name'))
        rel_landmark_type = gr.convert_result_elem_to_rdflib_elem(elem.get('ltype'))

        if rel_landmark_type == np.LTYPE["Thoroughfare"]:
            lm_label_type = "thoroughfare"
        elif rel_landmark_type in [np.LTYPE["Municipality"], np.LTYPE["District"]]:
            lm_label_type = "area"
        elif rel_landmark_type in [np.LTYPE["HouseNumber"],np.LTYPE["StreetNumber"],np.LTYPE["DistrictNumber"],np.LTYPE["PostalCodeArea"]]:
            lm_label_type = "housenumber"
        else:
            lm_label_type = None

        normalized_name, simplified_name = sp.normalize_and_simplify_name_version(rel_name.strip(), lm_label_type, rel_name.language)


        if normalized_name is not None:
            normalized_name_lit = Literal(normalized_name, lang=rel_name.language)
            query_lines += f"{rel_av.n3()} {SKOS.altLabel.n3()} {normalized_name_lit.n3()}.\n"
        if simplified_name is not None:
            simplified_name_lit = Literal(simplified_name, lang=rel_name.language)
            query_lines += f"{rel_av.n3()} {SKOS.hiddenLabel.n3()} {simplified_name_lit.n3()}.\n"

    query = np.query_prefixes + f"""
        INSERT DATA {{
            GRAPH {factoids_named_graph_uri.n3()} {{
                {query_lines}
            }}
        }}
        """

    gd.update_query(query, graphdb_url, repository_name)

def add_alt_and_hidden_labels_to_landmarks_from_name_attribute_versions(graphdb_url, repository_name, named_graph_uri:URIRef):
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{ ?lm skos:altLabel ?altLabel ; skos:hiddenLabel ?hiddenLabel . }}
        }}
        WHERE {{
            BIND({named_graph_uri.n3()} AS ?g)
            GRAPH ?g {{ ?lm a addr:Landmark }}
            ?lm addr:hasAttribute [a addr:Attribute; addr:isAttributeType atype:Name ; addr:hasAttributeVersion ?av ] .
            OPTIONAL {{ ?av skos:altLabel ?altLabel . }}
            OPTIONAL {{ ?av skos:hiddenLabel ?hiddenLabel . }}
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def merge_landmark_multiple_geometries(graphdb_url, repository_name, factoids_named_graph_uri, geom_kg_file):
    """
    Fusion des géométries d'un landmark si ce dernier en a plus d'une
    """

    to_remove_property = np.ADDR["toRemove"]

    # Query to select all landmark geometries
    query = np.query_prefixes + """
        SELECT DISTINCT * WHERE {
            ?attr addr:isAttributeType atype:Geometry ; addr:hasAttributeVersion ?attrVersion .
            ?attrVersion addr:versionValue ?geom .
            }
        """
    results = gd.select_query_to_json(query, graphdb_url, repository_name)

    attr_geom_values = {}

    for elem in results.get("results").get("bindings"):
        # Recovery of URIs (attribute and attribute version) and geometry
        rel_attr = gr.convert_result_elem_to_rdflib_elem(elem.get('attr'))
        rel_attr_version = gr.convert_result_elem_to_rdflib_elem(elem.get('attrVersion'))
        rel_geom = gr.convert_result_elem_to_rdflib_elem(elem.get('geom'))

        if rel_attr in attr_geom_values.keys():
            attr_geom_values[rel_attr].append([rel_attr_version, rel_geom])
        else:
            attr_geom_values[rel_attr] = [[rel_attr_version, rel_geom]]

    # Add a version of geometry which is the result of merging all the versions linked to an attribute.
    # Indicate for each initial version that it must be deleted.
    g = Graph()
    for attr_uri, versions in attr_geom_values.items():
        if len(versions) > 1:
            geoms = [version[1] for version in versions]
            wkt_literal = gp.get_union_of_geosparql_wktliterals(geoms)
            attr_version_uri = gr.generate_uri(np.FACTOIDS, "AV")
            gr.create_attribute_version(g, attr_version_uri, wkt_literal)
            gr.add_version_to_attribute(g, attr_uri, attr_version_uri)
            for version in versions:
                g.add((version[0], to_remove_property, Literal("true", datatype=XSD.boolean)))

    # Export the graph to the `kg_file` file, which is imported into the
    g.serialize(geom_kg_file)
    gd.import_ttl_file_in_graphdb(graphdb_url, repository_name, geom_kg_file, named_graph_uri=factoids_named_graph_uri)

    query = np.query_prefixes + f"""
        DELETE {{
            ?s ?p ?tmpResource.
            ?tmpResource ?p ?o.
        }}
        WHERE {{
            ?tmpResource {to_remove_property.n3()} ?toRemove.
            FILTER(?toRemove)
            {{?tmpResource ?p ?o}} UNION {{?s ?p ?tmpResource}}
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def transfert_immutable_triples(graphdb_url, repository_name, factoids_named_graph_uri, permanent_named_graph_uri):
    """
    All created triples via Ontotext-Refine are initially imported in factoids named graph.
    Some of them must be transfered in a permanent named graph, as they must not be modified while importing them in facts repository.
    """

    prefixes = np.query_prefixes + """
    PREFIX wb: <http://wikiba.se/ontology#>
    """

    # All triples whose predicate is `rico:isOrWasDescribedBy` are moved to permanent named graph
    query1 = prefixes + f"""
    DELETE {{
       ?s ?p ?o
    }}
    INSERT {{
        GRAPH {permanent_named_graph_uri.n3()} {{
            ?s ?p ?o.
        }}
    }}
    WHERE {{
        BIND(rico:isOrWasDescribedBy AS ?p)
        ?s ?p ?o.
    }} ;
    """

    # All triples whose subject is an URI and is a object of a triples whose predicate is `prov:wasDerivedFrom` are moved to permanent named graph
    query2 = prefixes + f"""
    DELETE {{
        GRAPH ?gf {{ ?prov ?p ?o }}
    }}
    INSERT {{
        GRAPH ?gp {{ ?prov ?p ?o }}
    }}
    WHERE
    {{
        BIND({factoids_named_graph_uri.n3()} AS ?gf)
        BIND({permanent_named_graph_uri.n3()} AS ?gp)
        GRAPH ?gf {{
            ?elem prov:wasDerivedFrom ?prov.
            ?prov ?p ?o.
        }}
    }}
    """

    # All triples whose subject is a Wikibase Item or Statement are moved to permanent named graph
    query3 = prefixes + f"""
    DELETE {{
        GRAPH ?gf {{ ?elem a ?type }}
    }}
    INSERT {{
        GRAPH ?gp {{ ?elem a ?type }}
    }}
    WHERE
    {{
        BIND({factoids_named_graph_uri.n3()} AS ?gf)
        BIND({permanent_named_graph_uri.n3()} AS ?gp)
        GRAPH ?gf {{
            ?elem a ?type.
        }}
        FILTER (?type in (wb:Item, wb:Statement))
    }}
    """

    queries = [query1, query2, query3]
    for query in queries:
        gd.update_query(query, graphdb_url, repository_name)

def create_factoid_repository(graphdb_url, repository_name, tmp_folder, ont_file, ontology_named_graph_name, ruleset_name=None, disable_same_as=False, clear_if_exists=False):
    """
    Initialisation of a repository to create a factoids graph

    `clear_if_exists` is a bool to remove all statements if repository already exists"
    """

    local_config_file_name = f"config_for_{repository_name}.ttl"
    local_config_file = os.path.join(tmp_folder, local_config_file_name)
    # Repository creation
    gd.create_repository(graphdb_url, repository_name, local_config_file, ruleset_file=None, ruleset_name=ruleset_name, disable_same_as=disable_same_as)

    if clear_if_exists:
        gd.clear_repository(graphdb_url, repository_name)

    gd.add_prefixes_to_repository(graphdb_url, repository_name, np.namespaces_with_prefixes)
    gd.import_ttl_file_in_graphdb(graphdb_url, repository_name, ont_file, ontology_named_graph_name)

def transfert_factoids_to_facts_repository(graphdb_url, facts_repository_name, factoids_repository_name,
                                           factoids_ttl_file, permanent_ttl_file,
                                           factoids_repo_factoids_named_graph_name, factoids_repo_permanent_named_graph_name,
                                           facts_repo_factoids_named_graph_name, facts_repo_facts_named_graph_name):
    """
    Transfer factoids to facts graph
    """

    gd.export_data_from_repository(graphdb_url, factoids_repository_name, factoids_ttl_file, factoids_repo_factoids_named_graph_name)
    gd.export_data_from_repository(graphdb_url, factoids_repository_name, permanent_ttl_file, factoids_repo_permanent_named_graph_name)
    gd.import_ttl_file_in_graphdb(graphdb_url, facts_repository_name, factoids_ttl_file, facts_repo_factoids_named_graph_name)
    gd.import_ttl_file_in_graphdb(graphdb_url, facts_repository_name, permanent_ttl_file, facts_repo_facts_named_graph_name)


####################################################################

## Management of root elements
"""
Cette partie inclut des fonctions pour créer des racines : chaque élément des graphes nommés qui incluent des factoïdes doit avoir un équivalent
dans le graphe nommé des faits. Cet équivalent est une racine (root). Une racine peut être l'équivalent de plusieurs éléments de plusieurs éléments.
Par exemple, s'il y a une "rue Gérard" dans plusieurs graphes nommés, ces derniers doivent être reliés à la même racine.
Les racines s'appliquent à Landmark, LandmarkRelation, Attribute, AttributeVersion, Event, Change, TemporalEntity.
"""

def create_roots_and_traces_for_landmarks(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef, inter_sources_name_graph_uri:URIRef):
    """
    Create `addr:hasRoot` links between similar landmarks.
    """

    create_roots_and_traces_for_landmark_areas(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)
    create_roots_and_traces_for_landmark_thoroughfares(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)
    create_roots_and_traces_for_landmark_housenumbers(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)
    create_roots_and_traces_for_landmark_others(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)

def create_roots_and_traces_for_landmark_areas(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef, inter_sources_name_graph_uri:URIRef):
    """
    Pour les repères de type DISTRICT, MUNICIPALITY ou POSTALCODEAREA définis dans le graphe nommé `factoids_named_graph_uri`, les lier avec un repère de même type défini dans `facts_named_graph_uri` s'ils ont un nom similaire.
    Le lien créé est mis dans `inter_sources_name_graph_uri`.
    """

    query = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{ ?rootLandmark a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel ; rdfs:label ?label . }}
        GRAPH ?gi {{
            ?landmark addr:hasRoot ?rootLandmark .
            ?rootLandmark addr:hasTrace ?landmark .
            
        }}
    }} WHERE {{
        BIND({facts_named_graph_uri.n3()} AS ?gf)
        BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
        BIND({factoids_named_graph_uri.n3()} AS ?gs)
        {{
            SELECT DISTINCT ?landmarkType ?keyLabel WHERE {{
                ?l a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel .
                FILTER(?landmarkType IN (ltype:Municipality, ltype:District, ltype:PostalCodeArea))
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "LM_", STRUUID())) AS ?toCreateRootLandmark)
        OPTIONAL {{ GRAPH ?gf {{?existingRootLandmark a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel .}}}}
        BIND(IF(BOUND(?existingRootLandmark), ?existingRootLandmark, ?toCreateRootLandmark) AS ?rootLandmark)
        GRAPH ?gs {{ ?landmark a addr:Landmark . }}
        ?landmark addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel ; rdfs:label ?label .
        MINUS {{ ?landmark addr:hasRoot ?rl . }}
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def create_roots_and_traces_for_landmark_thoroughfares(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef, inter_sources_name_graph_uri:URIRef):
    """
    Pour les repères de type VOIE définis dans le graphe nommé `factoids_named_graph_uri`, les lier avec un repère de même type défini dans `facts_named_graph_uri` s'ils ont un nom similaire.
    Le lien créé est mis dans `inter_sources_name_graph_uri`.
    """

    query = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{ ?rootLandmark a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel ; rdfs:label ?label . }}
        GRAPH ?gi {{
            ?landmark addr:hasRoot ?rootLandmark .
            ?rootLandmark addr:hasTrace ?landmark .
        }}
    }} WHERE {{
        BIND({facts_named_graph_uri.n3()} AS ?gf)
        BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
        BIND({factoids_named_graph_uri.n3()} AS ?gs)
        {{
            SELECT DISTINCT ?landmarkType ?keyLabel WHERE {{
                ?l a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel .
                FILTER(?landmarkType IN (ltype:Thoroughfare))
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "LM_", STRUUID())) AS ?toCreateRootLandmark)
        OPTIONAL {{ GRAPH ?gf {{?existingRootLandmark a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel .}}}}
        BIND(IF(BOUND(?existingRootLandmark), ?existingRootLandmark, ?toCreateRootLandmark) AS ?rootLandmark)
        GRAPH ?gs {{ ?landmark a addr:Landmark . }}
        ?landmark addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel ; rdfs:label ?label .
        MINUS {{ ?landmark addr:hasRoot ?rl . }}
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)


def create_roots_and_traces_for_landmark_housenumbers(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef, inter_sources_name_graph_uri:URIRef):
    """
    Pour les repères de type HOUSENUMBER définis dans le graphe nommé `factoids_named_graph_uri`, les lier avec un repère de même type défini dans `facts_named_graph_uri` s'ils ont un nom similaire.
    Le lien créé est mis dans `inter_sources_name_graph_uri`.
    """

    query = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{
            ?rootLandmark a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel ; rdfs:label ?label .
            ?rootLandmarkRelation a addr:LandmarkRelation ; addr:isLandmarkRelationType ?landmarkRelationType ; addr:locatum ?rootLandmark ; addr:relatum ?rootRelatum .
        }}
        GRAPH ?gi {{
            ?landmark addr:hasRoot ?rootLandmark .
            ?rootLandmark addr:hasTrace ?landmark .
            ?landmarkRelation addr:hasRoot ?rootLandmarkRelation .
            ?rootLandmarkRelation addr:hasTrace ?landmarkRelation .
        }}
    }}
    WHERE {{
        BIND({facts_named_graph_uri.n3()} AS ?gf)
        BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
        BIND({factoids_named_graph_uri.n3()} AS ?gs)
        {{
            SELECT DISTINCT ?landmarkType ?keyLabel ?landmarkRelationType ?rootRelatum WHERE {{
                ?lr a addr:LandmarkRelation ;
                addr:isLandmarkRelationType ?landmarkRelationType ;
                addr:locatum [a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel] ;
                addr:relatum [addr:hasRoot ?rootRelatum] .
                FILTER(?landmarkType IN (ltype:HouseNumber, ltype:StreetNumber, ltype:DistrictNumber))
                FILTER(?landmarkRelationType IN (lrtype:Belongs))
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "LM_", STRUUID())) AS ?toCreateRootLandmark)
        BIND(URI(CONCAT(STR(URI(facts:)), "LR_", STRUUID())) AS ?toCreateRootLR)
        OPTIONAL {{
            GRAPH ?gf {{
                ?existingRootLandmark a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel .
                ?existingRootLR a addr:LandmarkRelation ; addr:isLandmarkRelationType ?landmarkRelationType ;
                addr:locatum ?existingRootLandmark ; addr:relatum ?rootRelatum .
            }}
        }}
        BIND(IF(BOUND(?existingRootLandmark), ?existingRootLandmark, ?toCreateRootLandmark) AS ?rootLandmark)
        BIND(IF(BOUND(?existingRootLR), ?existingRootLR, ?toCreateRootLR) AS ?rootLandmarkRelation)
        GRAPH ?gs {{ ?landmark a addr:Landmark . }}
        ?landmark addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel ; rdfs:label ?label .
        ?landmarkRelation a addr:LandmarkRelation ; addr:isLandmarkRelationType ?landmarkRelationType ;
        addr:locatum ?landmark ; addr:relatum [addr:hasRoot ?rootRelatum] .
        MINUS {{ ?landmark addr:hasRoot ?rl . }}
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def create_roots_and_traces_for_landmark_others(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef, inter_sources_name_graph_uri:URIRef):
    """
    Pour les repères définis dans le graphe nommé `factoids_named_graph_uri` qui ne sont reliés à aucun repère dans le graphe `facts_named_graph_uri`,
    les lier avec un repère de même type créé dans `facts_named_graph_uri`.
    Le lien créé est mis dans `inter_sources_name_graph_uri`.
    """

    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{ ?rootLandmark a addr:Landmark ; addr:isLandmarkType ?landmarkType ; skos:hiddenLabel ?keyLabel ; rdfs:label ?label . }}
            GRAPH ?gi {{
                ?landmark addr:hasRoot ?rootLandmark .
                ?rootLandmark addr:hasTrace ?landmark .
            }}
        }}
        WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
            BIND({factoids_named_graph_uri.n3()} AS ?gs)
            {{
                SELECT DISTINCT ?gs ?landmark WHERE {{ GRAPH ?gs {{ ?landmark a addr:Landmark . }}}}
            }}
            BIND(URI(CONCAT(STR(URI(facts:)), "LM_", STRUUID())) AS ?rootLandmark)
            ?landmark addr:isLandmarkType ?landmarkType .
            OPTIONAL {{ ?landmark rdfs:label ?label }}
            OPTIONAL {{ ?landmark rdfs:label|skos:hiddenLabel ?hiddenLabel }}
            MINUS {{ ?landmark addr:hasRoot ?rl . }}
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

# TODO : modify it completely !
def create_roots_and_traces_for_temporal_entities(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri):
    # Create links for similar crisp time instants
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gi {{
                ?t1 addr:hasRoot ?t2.
                ?t2 addr:hasTrace ?t1.
            }}
        }}
        WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
            BIND({factoids_named_graph_uri.n3()} AS ?gs)
            GRAPH ?gs {{
                ?ev1 a addr:Event ; ?p ?t1 .
                ?t1 a addr:CrispTimeInstant .
                }}
            GRAPH ?gf {{
                ?ev2 a addr:Event ; ?p ?t2 .
                ?t2 a addr:CrispTimeInstant .
                }}
            FILTER (?p IN (addr:hasTime, addr:hasTimeBefore, addr:hasTimeAfter))
            ?t1 addr:timeStamp ?timeStamp ; addr:timeCalendar ?timeCal ; addr:timePrecision ?timePrec .
            ?t2 addr:timeStamp ?timeStamp ; addr:timeCalendar ?timeCal ; addr:timePrecision ?timePrec .
            ?ev1 addr:hasRoot ?ev2 .
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def create_roots_and_traces_for_landmark_relations(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef, inter_sources_name_graph_uri:URIRef):
    """
    Pour des relations entre repères dans le graphe nommé `factoids_named_graph_uri`, les lier avec une relation entre repères dans `facts_named_graph_uri` qui sont similaires (mêmes locatum, relatums et type de relation).
    Le lien créé est mis dans `factoids_facts_named_graph_uri`.
    """

    # Creation of a hiddenLabel for each LandmarkRelation in the (aggregation) fact graph. It is composed as follows: URI of the locatum + ‘&’ + ordered URIs of the relatums separated by a semicolon
    # For example, if a relationship has URILoc as its locatum and URIRel1 and URIRel2 as its relatums, the hidden label will be ‘URILoc1&URIRel1;URIRel2’.
    # We create this label for relationships that don't have one
    query1 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{?lr skos:hiddenLabel ?hiddenLabel}}
        }} WHERE {{
            {{
                SELECT ?gf ?lr (CONCAT(STR(?rootLoc), "|", GROUP_CONCAT(STR(?rootRel); separator=";")) AS ?hiddenLabel) WHERE {{
                    BIND({facts_named_graph_uri.n3()} AS ?gf)
                    GRAPH ?gf {{ ?lr a addr:LandmarkRelation . }}
                    ?lr addr:relatum ?rootRel ; addr:locatum ?rootLoc .
                }}
                GROUP BY ?gf ?lr ?rootLoc ORDER BY ?rootRel
            }}
        }}
    """

    # We do the same thing for the relations in the factoid graph. We don't integrate the URIs of the locatums and relatums, but the URIs of their root in the fact graph.
    query2 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gi {{?lr skos:hiddenLabel ?hiddenLabel}}
        }} WHERE {{
            BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
            {{
                SELECT ?gs ?lr (CONCAT(STR(?rootLoc), "|", GROUP_CONCAT(STR(?rootRel); separator=";")) AS ?hiddenLabel) WHERE {{
                    BIND({factoids_named_graph_uri.n3()} AS ?gs)
                    GRAPH ?gs {{ ?lr a ?lrClass . }}
                    ?lrClass rdfs:subClassOf addr:LandmarkRelation .
                    ?lr addr:relatum [addr:hasRoot ?rootRel] ; addr:locatum [addr:hasRoot ?rootLoc] .
                }}
                GROUP BY ?gs ?lr ?rootLoc ORDER BY ?rootRel
            }}
        }}
    """

    query3 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{ ?rootLandmarkRelation a addr:LandmarkRelation ; addr:isLandmarkRelationType ?landmarkRelationType ; skos:hiddenLabel ?keyLabel . }}
            GRAPH ?gi {{
                ?landmarkRelation addr:hasRoot ?rootLandmarkRelation .
                ?rootLandmarkRelation addr:hasTrace ?landmarkRelation .
            }}
        }}
        WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
            BIND({factoids_named_graph_uri.n3()} AS ?gs)
            {{
                SELECT DISTINCT ?landmarkRelationType ?keyLabel WHERE {{
                    ?lr a addr:LandmarkRelation ; addr:isLandmarkRelationType ?landmarkRelationType ; skos:hiddenLabel ?keyLabel .
                }}
            }}
            BIND(URI(CONCAT(STR(URI(facts:)), "LR_", STRUUID())) AS ?toCreateRootLR)
            OPTIONAL {{
                GRAPH ?gf {{ ?existingRootLR a addr:LandmarkRelation }}
                ?existingRootLR skos:hiddenLabel ?keyLabel .
            }}
            BIND(IF(BOUND(?existingRootLR), ?existingRootLR, ?toCreateRootLR) AS ?rootLandmarkRelation)
            GRAPH ?gs {{ ?landmarkRelation a ?lrClass . }}
            ?lrClass rdfs:subClassOf addr:LandmarkRelation .
            ?landmarkRelation addr:isLandmarkRelationType ?landmarkRelationType ; skos:hiddenLabel ?keyLabel .
        }}
    """

    query4 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{ ?rootLandmarkRelation ?prop ?rootLandmark . }}
        }}
        WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            GRAPH ?gf {{ ?rootLandmarkRelation a addr:LandmarkRelation .}}
            ?lr addr:hasRoot ?rootLandmarkRelation ; ?prop [addr:hasRoot ?rootLandmark] .
            FILTER (?prop IN (addr:locatum, addr:relatum))
        }}
    """

    queries = [query1, query2, query3, query4]
    for query in queries:
        gd.update_query(query, graphdb_url, repository_name)

def create_roots_and_traces_for_landmark_attributes(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef, inter_sources_name_graph_uri:URIRef):
    # Integration of changes in the fact graph (except for attribute changes, which are not unique)
    query = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{
            ?rootAttr a addr:Attribute ; addr:isAttributeType ?attrType .
            ?rootLandmark addr:hasAttribute ?rootAttr .
        }}
        GRAPH ?gi {{
            ?attr addr:hasRoot ?rootAttr .
            ?rootAttr addr:hasTrace ?attr .
            }}
    }} WHERE {{
        BIND({facts_named_graph_uri.n3()} AS ?gf)
        BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
        BIND({factoids_named_graph_uri.n3()} AS ?gs)
        {{
            SELECT DISTINCT ?attrType ?rootLandmark WHERE {{
                ?landmark addr:hasRoot ?rootLandmark ; addr:hasAttribute [a addr:Attribute ; addr:isAttributeType ?attrType] .
            }}
        }}

        GRAPH ?gs {{ ?attr a addr:Attribute . }}
        ?attr addr:isAttributeType ?attrType .
        ?landmark addr:hasRoot ?rootLandmark ; addr:hasAttribute ?attr .
        MINUS {{ ?attr addr:hasRoot ?x . }}
        OPTIONAL {{
            GRAPH ?gf {{ ?existingRootAttr a addr:Attribute . }}
            ?existingRootAttr addr:isAttributeType ?attrType .
            ?rootLandmark addr:hasAttribute ?existingRootAttr .
            }}
        BIND(IF(BOUND(?existingRootAttr), ?existingRootAttr, URI(CONCAT(STR(URI(facts:)), "ATTR_", STRUUID())) ) AS ?rootAttr)
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def create_roots_and_traces_for_landmark_attribute_versions(graphdb_url, facts_repository_name, facts_named_graph_uri, inter_sources_name_graph_uri, tmp_named_graph_uri):
    """
    Steps :
    1. After having sorted landmark versions and attribute version values, similar versions can be detected.
    These are linked together via <v1 addr:toBeMergedWith v2>. We need to remember to ensure that <v1 addr:toBeMergedWith v1>.
    This is done with `query1` and `query2`.

    2. It may be that more than two versions are similar to each other. To detect all the similar versions, we will associate them with a mergedVal constructed from the URIs of the similar versions.
    So if v1 is similar to v2, v3 and v4, the mergedVal will be ‘uriV1;uriV2;uriV3;uriV4’ where uriVi is the URI of version i. v2, v3 and v4 will have the same mergedVal.
    The triplet created will then be <v1 addr:hasMergedVal ‘uriV1;uriV2;uriV3;uriV4’>.
    This step is done with `query3`.

    3. We create a root attribute version for each group of similar versions, i.e. in the previous example, we will have vRoot which will be the root of v1, v2, v3 and v4.
    This is done with `query4`.

    4. Once the different versions have been created, you need to sort those that depend on the same attribute.
    For example, if we have v5 and v6 which have been grouped together via a vRootBis root and v4 precedes v5, we need to be able to say that vRoot precedes (`addr:precedes`) vRootBis.
    This is done with `query5`.

    5. Creating changes and events between successive attribute versions. In step 4, we deduced that vRoot preceded vRootBis.
    This means that there has been a change to the attribute linked to these versions.
    This change indicates a version change: vRoot is outdated (`addr:outdates`) while vRootBis is made effective (`addr:makesEffective`).
    This is done with `query6`.

    6. The triplets created in steps 1, 2 and 4 are deleted as they were just used for construction purposes.
    This is done with `query7`.
    """

    # Simple request to say that a version is similar to itself (must be merged with it)
    query1 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{
                ?vers addr:toBeMergedWith ?vers .
            }}
        }} WHERE {{
            BIND({tmp_named_graph_uri.n3()} AS ?g)
            ?vers a addr:AttributeVersion .
        }}
    """

    # Aggregation of successive versions with similar values (in several queries)
    # Add triples indicating similarity (addr:toBeMergedWith) with successive versions that have similar values (addr:hasNextVersion or addr:hasOverlappingVersion)
    query2 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{
                ?vers1 addr:toBeMergedWith ?vers2 .
                ?vers2 addr:toBeMergedWith ?vers1 .
            }}
        }} WHERE {{
            BIND({tmp_named_graph_uri.n3()} AS ?g)
            ?rootAttr a addr:Attribute ; addr:isRootOf ?attr1, ?attr2 .
            ?attr1 addr:hasAttributeVersion ?vers1 .
            ?attr2 addr:hasAttributeVersion ?vers2 .
            ?attr1 (addr:hasNextVersion|addr:hasOverlappingVersion) ?attr2 .
            ?vers1 addr:sameVersionValueAs ?vers2 .
            FILTER(!sameTerm(?attr1, ?attr2))
        }}
    """

    # Aggregation of successive versions with similar values (in several queries)
    # Add triples indicating similarity (addr:toBeMergedWith) with successive versions that have similar values (addr:hasNextVersion or addr:hasOverlappingVersion)
    query3 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{ ?vers1 addr:toBeMergedWith ?vers2 . }}
        }} WHERE {{
            BIND({tmp_named_graph_uri.n3()} AS ?g)
            ?vers1 addr:toBeMergedWith+ ?vers2 .
        }}
    """

    # For each version, we create a value (versMergeVal) which is the fusion of the URIs of versions that are similar.
    query4 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{ ?vers1 addr:versMergeVal ?versMergeVal }}
        }} WHERE {{
            BIND({tmp_named_graph_uri.n3()} AS ?g)
            {{
                SELECT ?vers1 (GROUP_CONCAT(STR(?vers2) ; separator="|") as ?versMergeVal) WHERE {{
                    ?vers1 addr:toBeMergedWith ?vers2 .
                }}
                GROUP BY ?vers1 ORDER BY ?vers2
            }}
        }}
    """

    # We create an attribute version that acts as a root (aggregation of similar versions)
    query5 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{
                ?rootAttrVers a addr:AttributeVersion .
                ?rootAttr addr:hasAttributeVersion ?rootAttrVers .
            }}
            GRAPH ?gi {{
                ?attrVers addr:hasRoot ?rootAttrVers .
                ?rootAttrVers addr:hasTrace ?attrVers .
            }}
        }} WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
            BIND(URI(CONCAT(STR(URI(facts:)), "AV_", STRUUID())) AS ?rootAttrVers)
            #BIND(URI(CONCAT(STR(URI(facts:)), "CG_", STRUUID())) AS ?cg)
            #BIND(URI(CONCAT(STR(URI(facts:)), "EV_", STRUUID())) AS ?ev)
            {{
                SELECT DISTINCT ?versMergeVal WHERE {{
                    ?vers addr:versMergeVal ?versMergeVal .
                }}
            }}
            ?attrVers addr:versMergeVal ?versMergeVal ; addr:isAttributeVersionOf [addr:hasRoot ?rootAttr] .
        }}
    """

    # We indicate that an attribute version 1 precedes an attribute version 2 if they have different values and if the landmark versions on which they depend follow one another.
    query6a = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gt {{
                [] a addr:ChangeDescription ; addr:appliedTo ?rootAttr ;
                addr:outdatedAttributeVersion ?rootAttrVers1 ; addr:madeEffectiveAttributeVersion ?rootAttrVers2 ;
                addr:hasTimeAfter ?startTime ; addr:hasTimeBefore ?endTime .
            }}
        }} WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            BIND({tmp_named_graph_uri.n3()} AS ?gt)
            BIND(URI(CONCAT(STR(URI(facts:)), "TMP_", STRUUID())) AS ?tmpChange)
            GRAPH ?gf {{ ?rootAttr a addr:Attribute . }}
            ?rootAttr addr:hasAttributeVersion ?rootAttrVers1, ?rootAttrVers2 .
            FILTER (?rootAttrVers1 != ?rootAttrVers2)
            ?rootAttrVers1 a addr:AttributeVersion ; addr:isRootOf [addr:isAttributeVersionOf ?attr1] .
            ?rootAttrVers2 a addr:AttributeVersion ; addr:isRootOf [addr:isAttributeVersionOf ?attr2] .
            ?attr1 (addr:hasNextVersion|addr:hasOverlappingVersion) ?attr2 .
            ?lm1 addr:hasAttribute ?attr1 ; addr:hasTime [addr:hasEnd ?endTime] .
            ?lm2 addr:hasAttribute ?attr2 ; addr:hasTime [addr:hasBeginning ?startTime] .
        }}
    """

    # We indicate that an attribute version is not preceded by any other, i.e. we indicate the appearance of the 1st (known) version.
    query6b = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gt {{
                [] a addr:ChangeDescription ; addr:appliedTo ?rootAttr ;
                addr:madeEffectiveAttributeVersion ?rootAttrVers ; addr:hasTimeBefore ?startTime .
            }}
        }} WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            BIND({tmp_named_graph_uri.n3()} AS ?gt)
            BIND(URI(CONCAT(STR(URI(facts:)), "TMP_", STRUUID())) AS ?tmpChange)
            GRAPH ?gf {{ ?rootAttr a addr:Attribute . }}
            ?rootAttr addr:hasAttributeVersion ?rootAttrVers .
            ?rootAttrVers a addr:AttributeVersion ; addr:isRootOf [addr:isAttributeVersionOf ?attr] .
            FILTER NOT EXISTS {{ ?x (addr:hasNextVersion|addr:hasOverlappingVersion) ?attr . }}
            ?lm addr:hasAttribute ?attr ; addr:hasTime [addr:hasBeginning ?startTime] .
        }}
    """

    # This indicates that one version of an attribute has not been succeeded by another, i.e. it indicates the disappearance of the last (known) version.
    query6c = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gt {{
                [] a addr:ChangeDescription ; addr:appliedTo ?rootAttr ;
                addr:outdatedAttributeVersion ?rootAttrVers ; addr:hasTimeAfter ?endTime .
            }}
        }} WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            BIND({tmp_named_graph_uri.n3()} AS ?gt)
            BIND(URI(CONCAT(STR(URI(facts:)), "TMP_", STRUUID())) AS ?tmpChange)
            GRAPH ?gf {{ ?rootAttr a addr:Attribute . }}
            ?rootAttr addr:hasAttributeVersion ?rootAttrVers .
            ?rootAttrVers a addr:AttributeVersion ; addr:isRootOf [addr:isAttributeVersionOf ?attr] .
            FILTER NOT EXISTS {{ ?attr (addr:hasNextVersion|addr:hasOverlappingVersion) ?x . }}
            ?lm addr:hasAttribute ?attr ; addr:hasTime [addr:hasEnd ?endTime] .
        }}
    """

    # Creating events and changes
    query7 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{
                ?rootTimeAfter a addr:CrispTimeInstant .
                ?rootTimeBefore a addr:CrispTimeInstant .
                ?rootEv a addr:Event ; addr:hasTimeAfter ?rootTimeAfter ; addr:hasTimeBefore ?rootTimeBefore.
                ?rootCg a addr:AttributeChange ; addr:isChangeType ctype:AttributeVersionTransition ;
                    addr:appliedTo ?rootAttr ; addr:dependsOn ?rootEv ;
                    addr:makesEffective ?rootAttrVers2 ; addr:outdates ?rootAttrVers1 .
            }}
            GRAPH ?gi {{
                ?timeAfter addr:hasRoot ?rootTimeAfter .
                ?timeBefore addr:hasRoot ?rootTimeBefore .
                ?rootTimeAfter addr:hasTrace ?timeAfter .
                ?rootTimeBefore addr:hasTrace ?timeBefore .
            }}
        }} WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
            ?changeDesc a addr:ChangeDescription ; addr:appliedTo ?rootAttr .
            OPTIONAL {{ ?changeDesc addr:outdatedAttributeVersion ?rootAttrVers1 . }}
            OPTIONAL {{ ?changeDesc addr:madeEffectiveAttributeVersion ?rootAttrVers2 . }}
            OPTIONAL {{ ?changeDesc addr:hasTimeAfter ?timeAfter . }}
            OPTIONAL {{ ?changeDesc addr:hasTimeBefore ?timeBefore . }}
            BIND(IF(BOUND(?changeDesc), URI(CONCAT(STR(URI(facts:)), "CG_", STRUUID())), ?x) AS ?rootCg)
            BIND(IF(BOUND(?changeDesc), URI(CONCAT(STR(URI(facts:)), "EV_", STRUUID())), ?x) AS ?rootEv)
            BIND(IF(BOUND(?timeAfter), URI(CONCAT(STR(URI(facts:)), "TI_", STRUUID())), ?x) AS ?rootTimeAfter)
            BIND(IF(BOUND(?timeBefore), URI(CONCAT(STR(URI(facts:)), "TI_", STRUUID())), ?x) AS ?rootTimeBefore)
            }}
    """

    queries = [query1, query2, query3, query4, query5, query6a, query6b, query6c, query7]
    for query in queries:
        gd.update_query(query, graphdb_url, facts_repository_name)

    # Deleting the temporary graph
    gd.remove_named_graph_from_uri(tmp_named_graph_uri)

def create_roots_and_traces_for_changes(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri):
    # Integration of changes in the fact graph (except for attribute changes, which are not unique)
    query = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{ ?rootChange a addr:Change ; addr:isChangeType ?changeType ; addr:appliedTo ?rootElem . }}
        GRAPH ?gi {{
            ?change addr:hasRoot ?rootChange .
            ?rootChange addr:hasTrace ?change .
        }}
    }} WHERE {{
        BIND({facts_named_graph_uri.n3()} AS ?gf)
        BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
        BIND({factoids_named_graph_uri.n3()} AS ?gs)
        {{
            SELECT DISTINCT ?changeType ?rootElem WHERE {{
                ?cg a addr:Change ; addr:isChangeType ?changeType ; addr:appliedTo [addr:hasRoot ?rootElem].
                MINUS {{ ?cg a addr:AttributeChange }}
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "CG_", STRUUID())) AS ?toCreateRootChange)
        OPTIONAL {{
            GRAPH ?gf {{ ?existingRootChange a addr:Change . }}
            ?existingRootChange addr:isChangeType ?changeType ; addr:appliedTo ?rootElem .
            }}
        BIND(IF(BOUND(?existingRootChange), ?existingRootChange, ?toCreateRootChange) AS ?rootChange)
        GRAPH ?gs {{ ?change a ?changeClass . }}
        ?changeClass rdfs:subClassOf addr:Change .
        ?change addr:isChangeType ?changeType ; addr:appliedTo [addr:hasRoot ?rootElem] .
        MINUS {{ ?change addr:hasRoot ?x . }}
    }}
    """
    gd.update_query(query, graphdb_url, repository_name)

def create_roots_and_traces_for_events(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri):
    # Integration of events in the fact graph
    # If two events have at least one change in common, they are considered to be equal (a change depends on only one event).
    query = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{
            ?rootEvent a addr:Event .
            ?rootChange addr:dependsOn ?rootEvent .
            }}
        GRAPH ?gi {{
            ?event addr:hasRoot ?rootEvent .
            ?rootEvent addr:hasTrace ?event .
        
        }}
    }} WHERE {{
        BIND({facts_named_graph_uri.n3()} AS ?gf)
        BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
        BIND({factoids_named_graph_uri.n3()} AS ?gs)
        {{
            SELECT DISTINCT ?rootChange WHERE {{
                ?ev a addr:Event ; addr:hasChange [addr:hasRoot ?rootChange] .
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "EV_", STRUUID())) AS ?toCreateRootEvent)
        OPTIONAL {{
            GRAPH ?gf {{?existingRootEvent a addr:Event . }}
            ?existingRootEvent addr:hasChange ?rootChange .
        }}
        BIND(IF(BOUND(?existingRootEvent), ?existingRootEvent, ?toCreateRootEvent) AS ?rootEvent)
        GRAPH ?gs {{ ?event a ?Event . }}
        ?event addr:hasChange [addr:hasRoot ?rootChange] .
        MINUS {{ ?event addr:hasRoot ?x . }}
    }}
    """
    gd.update_query(query, graphdb_url, repository_name)


####################################################################

## Temporal sorting and attribute version management
"""
This part includes functions for temporal sorting to manage attribute versions:
- temporal sorting of landmark state versions and attribute versions
- comparison of different versions of the same attribute. The comparison is based on their value (`<version addr:versionValue>`)
"""

def order_temporally_landmark_versions(graphdb_url, repository_name, order_named_graph_uri, tmp_named_graph_uri):
    # Calculating differences between landmark state versions
    query1 = np.query_prefixes + f"""
        PREFIX ofn: <http://www.ontotext.com/sparql/functions/>

        INSERT {{
            GRAPH ?g {{
                ?rootLm addr:hasTimeGap [ addr:hasValue ?timeGap ; addr:isFirstRL ?lm1 ; addr:isSecondRL ?lm2] .
            }}
        }}
        WHERE {{
            BIND({tmp_named_graph_uri.n3()} AS ?g)
            ?rootLm a addr:Landmark ; addr:isRootOf ?lm1, ?lm2.
            ?lm1 addr:hasTime [addr:hasEnd ?endTime1 ] .
            ?lm2 addr:hasTime [addr:hasBeginning ?startTime2 ] .
            ?endTime1 a addr:CrispTimeInstant ; addr:timeStamp ?endTimeStamp1 ; addr:timeCalendar ?timeCalendar.
            ?startTime2 a addr:CrispTimeInstant ; addr:timeStamp ?startTimeStamp2 ; addr:timeCalendar ?timeCalendar.
            BIND(ofn:asDays(?startTimeStamp2 - ?endTimeStamp1) as ?timeGap)
            FILTER (?timeGap > 0 && !sameTerm(?lm1, ?lm2))
        }}
        """

    # Detection of overlapping versions of landmark states
    query2 = np.query_prefixes + f"""
        PREFIX ofn: <http://www.ontotext.com/sparql/functions/>

        INSERT {{
            GRAPH ?go {{
                ?landmark addr:hasOverlappingVersion ?overlappedLandmark.
            }}
        }}
        WHERE {{
            BIND({order_named_graph_uri.n3()} AS ?go)
            ?rootLm a addr:Landmark ; addr:isRootOf ?landmark, ?overlappedLandmark.
            ?landmark addr:hasTime [addr:hasBeginning ?startTime1 ; addr:hasEnd ?endTime1 ] .
            ?overlappedLandmark addr:hasTime [addr:hasBeginning ?startTime2 ; addr:hasEnd ?endTime2 ] .
            ?startTime1 a addr:CrispTimeInstant ; addr:timeStamp ?startTimeStamp1 ; addr:timeCalendar ?timeCalendar.
            ?endTime1 a addr:CrispTimeInstant ; addr:timeStamp ?endTimeStamp1 ; addr:timeCalendar ?timeCalendar.
            ?startTime2 a addr:CrispTimeInstant ; addr:timeStamp ?startTimeStamp2 ; addr:timeCalendar ?timeCalendar.
            ?endTime2 a addr:CrispTimeInstant ; addr:timeStamp ?endTimeStamp2 ; addr:timeCalendar ?timeCalendar.
            BIND(ofn:asDays(?startTimeStamp1 - ?startTimeStamp2) AS ?diffStart)
            BIND(ofn:asDays(?endTimeStamp1 - ?endTimeStamp2) AS ?diffEnd)
            BIND(ofn:asDays(?endTimeStamp1 - ?startTimeStamp2) AS ?diffEnd1Start2)
            FILTER (((?diffEnd1Start2 > 0 && ((?diffStart < 0) || (?diffStart = 0 && ?diffEnd < 0))) ||
                    (?diffStart = 0 && ?diffEnd = 0)) &&
                !sameTerm(?landmark, ?overlappedLandmark))
        }}
        """

    # Detection of successive versions of landmark states
    query3 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?go {{
                ?landmark addr:hasNextVersion ?nextLandmark.
                ?nextLandmark addr:hasPreviousVersion ?landmark.
            }}
        }}
        WHERE {{
            BIND({order_named_graph_uri.n3()} AS ?go)
            # Sous-Requête pour récupérer les écarts minimums pour chaque landmark
            {{
                SELECT ?g ?landmark (MIN(?gapValue) AS ?minGapValue) WHERE {{
                    BIND({tmp_named_graph_uri.n3()} AS ?gt)
                    GRAPH ?gt {{
                        ?rlm addr:hasTimeGap [addr:hasValue ?gapValue ; addr:isFirstRL ?landmark].
                    }}
                }}
                GROUP BY ?g ?landmark
            }}
            GRAPH ?g {{
                ?rootLM addr:hasTimeGap [addr:hasValue ?minGapValue ; addr:isFirstRL ?landmark ; addr:isSecondRL ?nextLandmark] .
            }}
            FILTER NOT EXISTS {{ ?landmark addr:hasOverlappingVersion ?overlappedLandmark }}
            FILTER (!sameTerm(?landmark, ?nextLandmark))
        }}
    """

    queries = [query1, query2, query3]
    for query in queries:
        gd.update_query(query, graphdb_url, repository_name)

    # Deleting the temporary graph
    gd.remove_named_graph_from_uri(tmp_named_graph_uri)

def order_temporally_attribute_versions(graphdb_url, repository_name, order_named_graph_uri, tmp_named_graph_uri):
    # Calculation of differences between attribute status versions
    query1 = np.query_prefixes + f"""
        PREFIX ofn: <http://www.ontotext.com/sparql/functions/>

        INSERT {{
            GRAPH ?g {{
                ?rootAttr addr:hasTimeGap [ addr:hasValue ?timeGap ; addr:isFirstRL ?attr1 ; addr:isSecondRL ?attr2] .
            }}
        }}
        WHERE {{
            BIND({tmp_named_graph_uri.n3()} AS ?g)
            ?rootLm a addr:Landmark ; addr:hasAttribute ?rootAttr ; addr:isRootOf ?lm1, ?lm2.
            ?rootAttr a addr:Attribute ; addr:isRootOf ?attr1, ?attr2 .
            ?lm1 addr:hasAttribute ?attr1 .
            ?lm2 addr:hasAttribute ?attr2 .
            ?lm1 addr:hasTime [addr:hasEnd ?endTime1 ] .
            ?lm2 addr:hasTime [addr:hasBeginning ?startTime2 ] .
            ?endTime1 a addr:CrispTimeInstant ; addr:timeStamp ?endTimeStamp1 ; addr:timeCalendar ?timeCalendar.
            ?startTime2 a addr:CrispTimeInstant ; addr:timeStamp ?startTimeStamp2 ; addr:timeCalendar ?timeCalendar.
            BIND(ofn:asDays(?startTimeStamp2 - ?endTimeStamp1) as ?timeGap)
            FILTER (?timeGap > 0 && !sameTerm(?lm1, ?lm2))
        }}
        """

    # Detection of overlapping versions of attribute states
    query2 = np.query_prefixes + f"""
        PREFIX ofn: <http://www.ontotext.com/sparql/functions/>

        INSERT {{
            GRAPH ?go {{
                ?attr addr:hasOverlappingVersion ?overlappedAttr.
            }}
        }}
        WHERE {{
            BIND({order_named_graph_uri.n3()} AS ?go)
            ?rootAttr a addr:Attribute ; addr:isRootOf ?attr, ?overlappedAttr .
            ?landmark a addr:Landmark ; addr:hasAttribute ?attr ; addr:hasTime [addr:hasBeginning ?startTime1 ; addr:hasEnd ?endTime1 ] .
            ?overlappedLandmark a addr:Landmark ; addr:hasAttribute ?overlappedAttr ; addr:hasTime [addr:hasBeginning ?startTime2 ; addr:hasEnd ?endTime2 ] .
            ?startTime1 a addr:CrispTimeInstant ; addr:timeStamp ?startTimeStamp1 ; addr:timeCalendar ?timeCalendar.
            ?endTime1 a addr:CrispTimeInstant ; addr:timeStamp ?endTimeStamp1 ; addr:timeCalendar ?timeCalendar.
            ?startTime2 a addr:CrispTimeInstant ; addr:timeStamp ?startTimeStamp2 ; addr:timeCalendar ?timeCalendar.
            ?endTime2 a addr:CrispTimeInstant ; addr:timeStamp ?endTimeStamp2 ; addr:timeCalendar ?timeCalendar.
            BIND(ofn:asDays(?startTimeStamp1 - ?startTimeStamp2) AS ?diffStart)
            BIND(ofn:asDays(?endTimeStamp1 - ?endTimeStamp2) AS ?diffEnd)
            BIND(ofn:asDays(?endTimeStamp1 - ?startTimeStamp2) AS ?diffEnd1Start2)
            FILTER (((?diffEnd1Start2 > 0 && ((?diffStart < 0) || (?diffStart = 0 && ?diffEnd < 0))) ||
                    (?diffStart = 0 && ?diffEnd = 0)) &&
                !sameTerm(?landmark, ?overlappedLandmark))
        }}
        """

    # Detection of successive versions of attribute states
    query3 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?go {{
                ?attr addr:hasNextVersion ?nextAttr.
                ?nextAttr addr:hasPreviousVersion ?attr.
            }}
        }}
        WHERE {{
            BIND({order_named_graph_uri.n3()} AS ?go)
            # Sous-Requête pour récupérer les écarts minimums pour chaque attribut
            {{
                SELECT ?g ?attr (MIN(?gapValue) AS ?minGapValue) WHERE {{
                    BIND({tmp_named_graph_uri.n3()} AS ?gt)
                    GRAPH ?gt {{
                        ?rattr addr:hasTimeGap [addr:hasValue ?gapValue ; addr:isFirstRL ?attr].
                    }}
                }}
                GROUP BY ?g ?attr
            }}
            GRAPH ?g {{
                ?rootAttr addr:hasTimeGap [addr:hasValue ?minGapValue ; addr:isFirstRL ?attr ; addr:isSecondRL ?nextAttr] .
            }}
            FILTER NOT EXISTS {{ ?attr addr:hasOverlappingVersion ?overlappedAttr }}
            FILTER (!sameTerm(?attr, ?nextAttr))
        }}
    """

    queries = [query1, query2, query3]
    for query in queries:
        gd.update_query(query, graphdb_url, repository_name)

    # Deleting the temporary graph
    gd.remove_named_graph_from_uri(tmp_named_graph_uri)

####################################################################

def transfer_implicit_triples(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef):
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{ ?rootElem ?p ?o }}
        }} WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?gs)
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            ?rootElem addr:hasTrace ?elem .
            {{
                GRAPH ?gs {{ ?elemSource ?p ?oSource }}
                ?oRoot addr:hasTrace ?oSource .
                GRAPH ?gs {{ ?oSource a ?oSourceType }}
                GRAPH ?gf {{ ?oFact a ?oFactType }}
                BIND(?oFact AS ?o)
            }} UNION {{
                GRAPH ?gs {{ ?elemSource ?p ?oSource }}
                MINUS {{ GRAPH ?gs {{ ?oSource a ?oSourceType }} }}
                BIND(?oSource AS ?o)
            }}
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def transfer_version_values_to_roots(graphdb_url, repository_name, facts_named_graph_uri:URIRef):
    """
    Transfer attribute version values to root versions: if <?av addr:versionValue ?value> and <?rootAv addr:hasTrace ?av> then <?rootAv addr:versionValue ?value>.
    """

    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{ ?rootAttr addr:versionValue ?value }}
        }} WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            ?av addr:versionValue ?value ; addr:isTraceOf ?rootAttr .
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def transfer_provenances_to_roots(graphdb_url, repository_name, facts_named_graph_uri:URIRef):
    """
    Transférer les provenances (sources) des éléments vers leur racine
    """

    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{ ?rootElem prov:wasDerivedFrom ?provenance }}
        }} WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            ?elem prov:wasDerivedFrom ?provenance ; addr:isTraceOf ?rootElem .
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def transfer_crisp_time_instant_elements_to_roots(graphdb_url, repository_name, facts_named_graph_uri:URIRef):
    """
    Transfer the crisp time instant elements to their root.
    """

    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?gf {{ ?rootTime ?p ?timeElem }}
        }} WHERE {{
            BIND({facts_named_graph_uri.n3()} AS ?gf)
            ?time ?p ?timeElem ; addr:isTraceOf ?rootTime .
            FILTER(?p IN (addr:timeStamp, addr:timeCalendar, addr:timePrecision))
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def link_factoids_with_facts(graphdb_url, repository_name, factoids_named_graph_uri:URIRef, facts_named_graph_uri:URIRef, inter_sources_name_graph_uri:URIRef):
    """
    Landmarks are created as follows:
        * creation of links (using `addr:hasRoot`) between landmarks in the facts named graph and those which are in the factoid named graph ;
        * using inference rules, new `addr:hasRoot` links are deduced
        * for each resource defined in the factoids, we check whether it exists in the fact graph (if it is linked with a `addr:hasRoot` to a resource in the fact graph)
        * for unlinked factoid resources, we create its equivalent in the fact graph
    """

    create_roots_and_traces_for_landmarks(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)
    create_roots_and_traces_for_landmark_relations(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)
    create_roots_and_traces_for_landmark_attributes(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)

    # Les racines de modification sont créées sauf pour les modifications d'attributs.
    create_roots_and_traces_for_changes(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)
    create_roots_and_traces_for_events(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)

def import_factoids_in_facts(graphdb_url, repository_name, factoids_named_graph_name, facts_named_graph_name, inter_sources_name_graph_name):
    facts_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, facts_named_graph_name)
    factoids_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, factoids_named_graph_name)
    inter_sources_name_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, inter_sources_name_graph_name)

    # Addition of standardised and simplified labels for landmarks (on the factoid graph) in order to make links with fact landmarks
    add_alt_and_hidden_labels_to_landmarks(graphdb_url, repository_name, factoids_named_graph_uri)

    link_factoids_with_facts(graphdb_url, repository_name, factoids_named_graph_uri, facts_named_graph_uri, inter_sources_name_graph_uri)

def infer_missing_changes_on_landmark_and_relations(graphdb_url, facts_repository_name, facts_named_graph_uri):

    # Create a change (appearance and/or disappearance) for landmarks and landmark relations for which change is missing.
    # Associate this change with an event. Tell the event has no time which has to be added (?event addr:timeToAdd "true"^^xsd:boolean)
    # Related time will be added by the next query.
    query = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{
            ?change a addr:Change ; addr:isChangeType ?cgType ; addr:appliedTo ?elem ; addr:dependsOn ?event .
            ?event a addr:Event .
        }}
    }} WHERE {{
        {{
            SELECT DISTINCT * WHERE {{
                BIND({facts_named_graph_uri.n3()} AS ?gf)
                VALUES (?cgType ?class) {{
                    (ctype:LandmarkAppearance addr:Landmark)
                    (ctype:LandmarkDisappearance addr:Landmark)
                    (ctype:LandmarkRelationAppearance addr:LandmarkRelation)
                    (ctype:LandmarkRelationDisappearance addr:LandmarkRelation)
                }}
                GRAPH ?gf {{?elem a ?elemClass}}
                ?elemClass rdfs:subClassOf ?class .
                FILTER NOT EXISTS {{?change a [rdfs:subClassOf addr:Change] ; addr:isChangeType ?cgType ; addr:appliedTo ?elem . }}
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "CG_", STRUUID())) AS ?change)
        BIND(URI(CONCAT(STR(URI(facts:)), "EV_", STRUUID())) AS ?event)
    }}
    """

    gd.update_query(query, graphdb_url, facts_repository_name)


def infer_missing_time_on_events(graphdb_url, facts_repository_name, facts_named_graph_uri, inter_sources_name_graph_uri):
    # For events created from no factoid (event without any trace: `FILTER NOT EXISTS {{ ?rootEvent addr:hasTrace ?randomEvent . }}`) and containing changes applied to landmark and landmark relation, we deduce time thanks to landmark versions.
    # We deduce the event related to the appearance of a landmark or a landmark relation appears before the beginning of the interval of the first version (versions are already ordered temporally).
    # We deduce the event related to the disapearance of a landmark or a landmark relation appears after the end of the interval of the last version.
    query1a = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{
            ?rootEvent addr:hasTimeBefore ?rootInstant .
            ?rootInstant a addr:CrispTimeInstant .
        }}
        GRAPH ?gi {{
            ?rootInstant addr:hasTrace ?instant .
            ?instant addr:hasRoot ?rootInstant .
        }}
    }} WHERE {{
        {{
            SELECT DISTINCT * WHERE {{
                BIND({facts_named_graph_uri.n3()} AS ?gf)
                BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
                VALUES ?cgType {{ ctype:LandmarkAppearance ctype:LandmarkRelationAppearance }}
                GRAPH ?gf {{ ?rootEvent a addr:Event . }}
                ?rootEvent addr:hasChange [addr:isChangeType ?cgType ; addr:appliedTo [addr:hasTrace ?elem] ] .
                ?elem addr:hasTime [addr:hasBeginning ?instant] .
                FILTER NOT EXISTS {{ ?rootEvent addr:hasTrace ?randomEvent . }}
                FILTER NOT EXISTS {{ ?elem addr:hasPreviousVersion|addr:isOverlappedByVersion ?randomElem . }}
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "TI_", STRUUID())) AS ?rootInstant)
    }}
    """

    query1b = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{
            ?rootEvent addr:hasTimeAfter ?rootInstant .
            ?rootInstant a addr:CrispTimeInstant .
        }}
        GRAPH ?gi {{
            ?rootInstant addr:hasTrace ?instant .
            ?instant addr:hasRoot ?rootInstant .
        }}
    }} WHERE {{
        {{
            SELECT DISTINCT * WHERE {{
                BIND({facts_named_graph_uri.n3()} AS ?gf)
                BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
                VALUES ?cgType {{ ctype:LandmarkDisappearance ctype:LandmarkRelationDisappearance }}
                GRAPH ?gf {{ ?rootEvent a addr:Event . }}
                ?rootEvent addr:hasChange [addr:isChangeType ?cgType ; addr:appliedTo [addr:hasTrace ?elem] ] .
                ?elem addr:hasTime [addr:hasEnd ?instant] .
                FILTER NOT EXISTS {{ ?rootEvent addr:hasTrace ?randomEvent . }}
                FILTER NOT EXISTS {{ ?elem addr:hasNextVersion|addr:hasOverlappingVersion ?randomElem . }}
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "TI_", STRUUID())) AS ?rootInstant)
    }}
    """

    query2 = np.query_prefixes + f"""
    INSERT {{
        GRAPH ?gf {{
            ?rootInstant a addr:CrispTimeInstant .
            ?rootEvent addr:hasTime ?rootInstant .
        }}
        GRAPH ?gi {{
            ?rootInstant addr:hasTrace ?instant .
        }}
    }} WHERE {{
        {{
            SELECT DISTINCT ?gf ?gi ?rootEvent WHERE {{
                BIND({facts_named_graph_uri.n3()} AS ?gf)
                BIND({inter_sources_name_graph_uri.n3()} AS ?gi)
                GRAPH ?gf {{
                    ?rootEvent a addr:Event .
                    FILTER NOT EXISTS {{ ?rootEvent addr:hasTime ?rootInstant }}
                }}
            }}
        }}
        BIND(URI(CONCAT(STR(URI(facts:)), "TI_", STRUUID())) AS ?rootInstant)
        ?rootEvent addr:hasTrace [addr:hasTime ?instant] .
    }}
    """
    print(query2)

    queries = [query1a, query1b, query2]
    for query in queries:
        gd.update_query(query, graphdb_url, facts_repository_name)

####################################################################

## Creation sources

def create_source_resource(graphdb_url, repository_name, source_uri:URIRef, source_label:str, publisher_label:str, lang:str, namespace:Namespace, named_graph_uri:URIRef):
    """
    Creation of the source for a resource
    """

    source_label_lit = Literal(source_label, lang=lang)
    query = np.query_prefixes + f"""
        INSERT DATA {{
            GRAPH {named_graph_uri.n3()} {{
                {source_uri.n3()} a rico:Record ; rdfs:label {source_label_lit.n3()} .
            }}
        }}
    """
    gd.update_query(query, graphdb_url, repository_name)

    if publisher_label is not None:
        publisher_uri = gr.generate_uri(namespace, "PUB")
        publisher_label_lit = Literal(publisher_label, lang=lang)
        query = np.query_prefixes + f"""
        INSERT DATA {{
            GRAPH {named_graph_uri.n3()} {{
                {source_uri.n3()} rico:hasPublisher {publisher_uri.n3()} .
                {publisher_uri.n3()} a rico:CorporateBody;
                    rdfs:label {publisher_label_lit.n3()}.
            }}
        }}
        """
        gd.update_query(query, graphdb_url, repository_name)

def link_provenances_with_source(graphdb_url, repository_name, source_uri:URIRef, named_graph_uri:URIRef):
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH {named_graph_uri.n3()} {{
                ?prov rico:isOrWasDescribedBy ?sourceUri .
            }}
        }} WHERE {{
            BIND({named_graph_uri.n3()} AS ?g)
            BIND({source_uri.n3()} AS ?sourceUri)
            GRAPH ?g {{
                ?prov a prov:Entity .
            }}
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)


def create_landmark_version(g:Graph, lm_uri:URIRef, lm_type_uri:URIRef, lm_label:str, attr_types_and_values:list[list], time_description:dict, provenance_uri:URIRef, factoids_namespace:Namespace, lang:str):
    gr.create_landmark(g, lm_uri, lm_label, lang, lm_type_uri)

    for attr in attr_types_and_values:
        attr_type_uri, attr_value_lit = attr
        attr_uri, attr_version_uri = gr.generate_uri(factoids_namespace, "ATTR"), gr.generate_uri(factoids_namespace, "AV")
        gr.create_landmark_attribute_and_version(g, lm_uri, attr_uri, attr_type_uri, attr_version_uri, attr_value_lit)

        # Add provenance (if supplied)
        if provenance_uri is not None:
            gr.add_provenance_to_resource(g, attr_version_uri, provenance_uri)

        # If the attribute is of type `Name`, we add alternative labels to its versions.
        if attr_type_uri in [np.ATYPE["Name"]]:
            attr_value_lit_label, attr_value_lit_lang = attr_value_lit.value, attr_value_lit.language
            add_other_labels_for_resource(g, attr_version_uri, attr_value_lit_label, attr_value_lit_lang, lm_type_uri)

    # Adding alternative labels for the landmark
    add_other_labels_for_resource(g, lm_uri, lm_label, lang, lm_type_uri)
    add_validity_time_interval_to_landmark(g, lm_uri, time_description)

    if provenance_uri is not None:
        gr.add_provenance_to_resource(g, lm_uri, provenance_uri)


def detect_similar_landmarks_with_hidden_label_and_landmark_relation(graphdb_url, repository_name, similar_property:URIRef, landmark_type:URIRef, landmark_relation_type:URIRef, factoids_named_graph_uri:URIRef):
    # Detection of similar landmarks on the sole criterion of hiddenlabel similarity and belonging to the same landmark (they must have the same type)
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{ ?landmark {similar_property.n3()} ?tmpLandmark . }}
        }}
        WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
            {{
                SELECT DISTINCT ?hiddenLabel ?belongsLandmark {{
                    ?tmpLandmark a addr:Landmark; addr:isLandmarkType {landmark_type.n3()} ; skos:hiddenLabel ?hiddenLabel .
                    ?lr a addr:LandmarkRelation ; addr:isLandmarkRelationType {landmark_relation_type.n3()}; addr:locatum ?tmpLandmark ; addr:relatum ?belongsLandmark .
                }}
            }}
        BIND(URI(CONCAT(STR(URI(factoids:)), "LM_", STRUUID())) AS ?landmark)
        ?tmpLandmark a addr:Landmark; addr:isLandmarkType {landmark_type.n3()} ; skos:hiddenLabel ?hiddenLabel.
        ?lr a addr:LandmarkRelation ; addr:isLandmarkRelationType {landmark_relation_type.n3()}; addr:locatum ?tmpLandmark ; addr:relatum ?belongsLandmark .
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def detect_similar_landmarks_with_hidden_label(graphdb_url, repository_name, similar_property:URIRef, landmark_type:URIRef, factoids_named_graph_uri:URIRef):
    # Detection of similar landmarks based solely on the hiddenlabel similarity criterion (they must have the same type)
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{ ?landmark {similar_property.n3()} ?tmpLandmark . }}
        }}
        WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
            {{
                SELECT DISTINCT ?hiddenLabel {{
                    ?tmpLandmark a addr:Landmark; addr:isLandmarkType {landmark_type.n3()} ; skos:hiddenLabel ?hiddenLabel.
                }}
            }}
        BIND(URI(CONCAT(STR(URI(factoids:)), "LM_", STRUUID())) AS ?landmark)
        ?tmpLandmark a addr:Landmark; addr:isLandmarkType {landmark_type.n3()} ; skos:hiddenLabel ?hiddenLabel.
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def detect_similar_landmark_versions_with_hidden_label(graphdb_url, repository_name, similar_property, landmark_type, factoids_named_graph_uri):
    # Detection of similar landmarks based solely on the hiddenlabel similarity criterion (they must have the same type).
    # To be considered as a version of a landmark, the landmark must be the subject of a triplet of the type `<?s addr:hasTime ?o>`.
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{ ?landmark {similar_property.n3()} ?tmpLandmark . }}
        }}
        WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
            {{
                SELECT DISTINCT ?hiddenLabel {{
                    ?tmpLandmark a addr:Landmark; addr:isLandmarkType {landmark_type.n3()} ; skos:hiddenLabel ?hiddenLabel.
                }}
            }}
        BIND(URI(CONCAT(STR(URI(factoids:)), "LM_", STRUUID())) AS ?landmark)
        ?tmpLandmark a addr:Landmark; addr:isLandmarkType {landmark_type.n3()} ; skos:hiddenLabel ?hiddenLabel ; addr:hasTime ?x.
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def detect_similar_attributes(graphdb_url, repository_name, similar_property:URIRef, factoids_named_graph_uri:URIRef):
    # Detection of similar attributes from the previous query
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{
                ?attr {similar_property.n3()} ?tmpAttr .
            }}
        }} WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
            {{
                SELECT DISTINCT ?lm ?attrType WHERE {{
                    ?lm addr:hasAttribute [addr:isAttributeType ?attrType] .
                }}
            }}
            BIND(URI(CONCAT(STR(URI(factoids:)), "ATTR_", STRUUID())) AS ?attr)
            ?lm addr:hasAttribute ?tmpAttr .
            ?tmpAttr addr:isAttributeType ?attrType .
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)


def detect_similar_attribute_versions(graphdb_url, repository_name, similar_property:URIRef, factoids_named_graph_uri:URIRef):
    query = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{
                ?av {similar_property.n3()} ?tmpAv .
            }}
        }} WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
            {{
                SELECT DISTINCT ?attr ?versionValue WHERE {{
                    ?attr addr:hasAttributeVersion [addr:versionValue ?versionValue] .
                }}
            }}
            BIND(URI(CONCAT(STR(URI(factoids:)), "AV_", STRUUID())) AS ?av)
            ?attr addr:hasAttributeVersion ?tmpAv .
            ?tmpAv addr:versionValue ?versionValue .
        }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def detect_similar_landmark_relations(graphdb_url, repository_name, similar_property:URIRef, factoids_named_graph_uri:URIRef):
    query = np.query_prefixes + f"""
    INSERT {{
        GRAPH {factoids_named_graph_uri.n3()} {{
            ?lr1 {similar_property.n3()} ?lr2 .
        }}
    }}
    WHERE {{
        BIND({factoids_named_graph_uri.n3()} AS ?gs)
        ?lr1 a addr:LandmarkRelation ; addr:isLandmarkRelationType ?lrtype ; addr:locatum ?loc ; addr:relatum ?rel .
        ?lr2 a addr:LandmarkRelation ; addr:isLandmarkRelationType ?lrtype ; addr:locatum ?loc ; addr:relatum ?rel .
        FILTER (!sameTerm(?lr1, ?lr2))
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def merge_similar_landmarks_with_hidden_labels(graphdb_url, repository_name, landmark_type:URIRef, factoids_named_graph_uri:URIRef):
    similar_property = np.SKOS["exactMatch"]

    # Detection and merging of similar landmarks
    detect_similar_landmarks_with_hidden_label(graphdb_url, repository_name, similar_property, landmark_type, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

    # Detection and merging of similar attributes
    detect_similar_attributes(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

    # Detection and merging of similar attribute versions
    detect_similar_attribute_versions(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

def merge_similar_landmark_versions_with_hidden_labels(graphdb_url, repository_name, landmark_type:URIRef, factoids_named_graph_uri:URIRef):
    similar_property = np.SKOS["exactMatch"]

    # Detection and merging of similar landmarks
    detect_similar_landmark_versions_with_hidden_label(graphdb_url, repository_name, similar_property, landmark_type, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

    # Detection and merging of similar attributes
    detect_similar_attributes(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

    # Detection and merging of similar attribute versions
    detect_similar_attribute_versions(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

def merge_similar_landmarks_with_hidden_label_and_landmark_relation(graphdb_url, repository_name, landmark_type:URIRef, landmark_relation_type:URIRef, factoids_named_graph_uri:URIRef):
    similar_property = np.SKOS["exactMatch"]

    # Detection and merging of similar landmarks
    detect_similar_landmarks_with_hidden_label_and_landmark_relation(graphdb_url, repository_name, similar_property, landmark_type, landmark_relation_type, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

    # Detection and merging of similar attributes
    detect_similar_attributes(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

    # Detection and merging of similar attribute versions
    detect_similar_attribute_versions(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

def merge_similar_landmark_relations(graphdb_url, repository_name, factoids_named_graph_uri:URIRef):
    similar_property = np.SKOS["exactMatch"]

    # Detection and merging of similar landmark relations
    detect_similar_landmark_relations(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)
    remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, similar_property, factoids_named_graph_uri)

def detect_similar_time_interval_of_landmarks(graphdb_url, repository_name, similar_property, factoids_named_graph_uri:URIRef):
    query1 = np.query_prefixes  + f"""
        INSERT {{
            ?lm addr:hasTime ?time .
            ?time a addr:TemporaryTime .
        }}
        WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
            {{
                SELECT DISTINCT ?lm ?time WHERE {{
                    ?lm a addr:Landmark .
                }}
            }}
            BIND(URI(CONCAT(STR(URI(factoids:)), "TI_", STRUUID())) AS ?time)
        }} ;

        DELETE {{
            ?time a addr:TemporaryTime .
            ?lm addr:hasTime ?time .
        }}
        INSERT {{
            GRAPH ?g {{ ?time {similar_property.n3()} ?tmpTime . }}
        }}
        WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
            ?lm addr:hasTime ?tmpTime , ?time .
            ?time a addr:TemporaryTime .
            FILTER(?tmpTime != ?time)
        }}
    """

    query2 = np.query_prefixes + f"""
        INSERT {{
            GRAPH ?g {{ ?time {similar_property.n3()} ?tmpTime . }}
        }}
        WHERE {{
            BIND({factoids_named_graph_uri.n3()} AS ?g)
        {{
            SELECT DISTINCT ?propTime ?timeStamp ?timeCal ?timePrec WHERE {{
                ?interval a addr:CrispTimeInterval ; ?propTime ?time .
                FILTER(?propTime IN (addr:hasBeginning, addr:hasEnd))
                ?time addr:timeStamp ?timeStamp ; addr:timeCalendar ?timeCal ; addr:timePrecision ?timePrec .
            }}
        }}
        BIND(URI(CONCAT(STR(URI(factoids:)), "TI_", STRUUID())) AS ?time)
        ?interval a addr:CrispTimeInterval ; ?propTime ?tmpTime.
    }}
    """

    queries = [query1, query2]
    for query in queries:
        gd.update_query(query, graphdb_url, repository_name)
        remove_temporary_resources_and_transfert_triples(graphdb_url, repository_name, np.SKOS["exactMatch"], factoids_named_graph_uri)


def remove_temporary_resources_and_transfert_triples(graphdb_url:str, repository_name:str, similar_property:URIRef, named_graph_uri:str):
    """
    Deletion of temporary resources and transfer of all their triplets to their associated resource (such as `<?resource skos:exactMatch ?temporaryResource>`).
    """
    query = np.query_prefixes + f"""
    DELETE {{
        GRAPH ?g {{
            ?s ?p ?tmpResource.
            ?tmpResource ?p ?o.
        }}
    }}
    INSERT {{
        GRAPH ?g {{
            ?s ?p ?resource.
            ?resource ?p ?o.
        }}
    }}
    WHERE {{
        ?resource {similar_property.n3()} ?tmpResource.
        GRAPH ?g {{
            {{?tmpResource ?p ?o}} UNION {{?s ?p ?tmpResource}}
          }}
    }} ;

    DELETE {{
        ?resource {similar_property.n3()} ?tmpResource.
    }}
    WHERE {{
        BIND({named_graph_uri.n3()} AS ?g)
        GRAPH ?g {{
            ?resource {similar_property.n3()} ?tmpResource.
        }}
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def add_other_labels_for_resource(g:Graph, res_uri:URIRef, res_label_value:str, res_label_lang:str, res_type_uri:URIRef):
    if res_type_uri == np.LTYPE["Thoroughfare"]:
        res_label_type = "thoroughfare"
    elif res_type_uri in [np.LTYPE["Municipality"], np.LTYPE["District"]]:
        res_label_type = "area"
    elif res_type_uri in [np.LTYPE["HouseNumber"],np.LTYPE["StreetNumber"],np.LTYPE["DistrictNumber"],np.LTYPE["PostalCodeArea"]]:
        res_label_type = "housenumber"
    else:
        res_label_type = None

    # Adding alternative and hidden labels
    alt_label, hidden_label = sp.normalize_and_simplify_name_version(res_label_value, res_label_type, res_label_lang)

    if alt_label is not None:
        alt_label_lit = Literal(alt_label, lang=res_label_lang)
        g.add((res_uri, SKOS.altLabel, alt_label_lit))

    if hidden_label is not None:
        hidden_label_lit = Literal(hidden_label, lang=res_label_lang)
        g.add((res_uri, SKOS.hiddenLabel, hidden_label_lit))


def transfert_rdflib_graph_to_factoids_repository(graphdb_url, repository_name, factoids_named_graph_name:str, g:Graph, kg_file:str, tmp_folder, ont_file, ontology_named_graph_name):
    g.serialize(kg_file)

    # Creating repository
    create_factoid_repository(graphdb_url, repository_name, tmp_folder,
                                ont_file, ontology_named_graph_name, ruleset_name="rdfsplus-optimized",
                                disable_same_as=False, clear_if_exists=True)

    # Import the `kg_file` file into the directory
    gd.import_ttl_file_in_graphdb(graphdb_url, repository_name, kg_file, factoids_named_graph_name)

def add_validity_time_interval_to_landmark(g:Graph, lm_uri:URIRef, time_description:dict):
    start_time_stamp, start_time_calendar, start_time_precision = tp.get_time_instant_elements(time_description.get("start_time"))
    end_time_stamp, end_time_calendar, end_time_precision = tp.get_time_instant_elements(time_description.get("end_time"))
    time_interval_uri, start_time_uri, end_time_uri = gr.generate_uri(np.FACTOIDS, "TI"), gr.generate_uri(np.FACTOIDS, "TI"), gr.generate_uri(np.FACTOIDS, "TI")

    gr.create_crisp_time_instant(g, start_time_uri, start_time_stamp, start_time_calendar, start_time_precision)
    gr.create_crisp_time_instant(g, end_time_uri, end_time_stamp, end_time_calendar, end_time_precision)
    gr.create_crisp_time_interval(g, time_interval_uri, start_time_uri, end_time_uri)
    gr.add_time_to_resource(g, lm_uri, time_interval_uri)