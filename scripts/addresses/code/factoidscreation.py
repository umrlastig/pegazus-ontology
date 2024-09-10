import json
import re
from rdflib import Graph, RDFS, Literal, URIRef, Namespace, XSD
from rdflib.namespace import RDF, XSD, RDFS, SKOS
from namespaces import NameSpaces
import geomprocessing as gp
import filemanagement as fm
import strprocessing as sp
import timeprocessing as tp
import multisourcesprocessing as msp
import wikidata as wd
import graphdb as gd
import graphrdf as gr

np = NameSpaces()

## Données de la BAN

def create_factoids_repository_ban(graphdb_url, ban_repository_name, tmp_folder,
                                   ont_file, ontology_named_graph_name,
                                   factoids_named_graph_name, permanent_named_graph_name,
                                   ban_csv_file, ban_kg_file, ban_time_description={}, lang=None):

    # Création d'un graphe basique avec rdflib et export dans le fichier `ban_kg_file`
    g = create_graph_from_ban(ban_csv_file, ban_time_description, lang)

    # Export du graphe et import de ce dernier dans le répertoire
    msp.transfert_rdflib_graph_to_factoids_repository(graphdb_url, ban_repository_name, factoids_named_graph_name, g, ban_kg_file, tmp_folder, ont_file, ontology_named_graph_name)

    # Adaptation des données avec l'ontologie, fusion de doublons...
    clean_repository_ban(graphdb_url, ban_repository_name, factoids_named_graph_name, permanent_named_graph_name, lang)

def create_graph_from_ban(ban_file, source_time_description:dict, lang:str):
    ban_pref, ban_ns = "ban", Namespace("https://adresse.data.gouv.fr/base-adresse-nationale/")
    source_time_description = tp.get_valid_time_description(source_time_description)

    ## Colonnes du fichier BAN
    hn_id_col, hn_number_col, hn_rep_col, hn_lon_col, hn_lat_col = "id", "numero", "rep", "lon", "lat"
    th_name_col, th_fantoir_col = "nom_voie",  "id_fantoir"
    cp_number_col = "code_postal"
    arrdt_name_col, arrdt_insee_col = "nom_commune", "code_insee"

    content = fm.read_csv_file_as_dict(ban_file, id_col=hn_id_col, delimiter=";", encoding='utf-8-sig')
    g = Graph()
    gr.add_namespaces_to_graph(g, np.namespaces_with_prefixes)
    g.bind(ban_pref, ban_ns)

    for value in content.values():
        hn_id = value.get(hn_id_col)
        hn_label = value.get(hn_number_col) + value.get(hn_rep_col)
        hn_geom = "POINT (" + value.get(hn_lon_col) + " " + value.get(hn_lat_col) + ")"
        th_label = value.get(th_name_col)
        th_id = value.get(th_fantoir_col)
        cp_label = value.get(cp_number_col)
        arrdt_label = value.get(arrdt_name_col)
        arrdt_id = value.get(arrdt_insee_col)

        create_data_value_from_ban(g, ban_ns, hn_id, hn_label, hn_geom, th_id, th_label, cp_label, arrdt_id, arrdt_label, source_time_description, lang)

    return g

def clean_repository_ban(graphdb_url, repository_name, factoids_named_graph_name, permanent_named_graph_name, lang):
    factoids_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, factoids_named_graph_name)
    permanent_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, permanent_named_graph_name)

    # Détection des arrondissements et quartiers qui ont un hiddenLabel similaire
    # Faire de même avec les codes postaux et les voies
    landmark_types = [np.LTYPE["District"], np.LTYPE["PostalCodeArea"], np.LTYPE["Thoroughfare"]]
    for ltype in landmark_types:
        msp.merge_similar_landmarks_with_hidden_labels(graphdb_url, repository_name, ltype, factoids_named_graph_uri)

    msp.merge_similar_landmark_relations(graphdb_url, repository_name, factoids_named_graph_uri)
    msp.detect_similar_time_interval_of_landmarks(graphdb_url, repository_name, np.SKOS["exactMatch"], factoids_named_graph_uri)

    # Transférer toutes les descriptions de provenance vers le graphe nommé permanent
    msp.transfert_immutable_triples(graphdb_url, repository_name, factoids_named_graph_uri, permanent_named_graph_uri)

    # L'URI ci-dessous définit la source liée à la ville de Paris
    vdp_source_uri = np.FACTS["Source_BAN"]
    source_label = "Base Adresse Nationale"
    publisher_label = "DINUM / ANCT / IGN"
    msp.create_source_resource(graphdb_url, repository_name, vdp_source_uri, source_label, publisher_label, lang, np.FACTS, permanent_named_graph_uri)
    msp.link_provenances_with_source(graphdb_url, repository_name, vdp_source_uri, permanent_named_graph_uri)

def create_data_value_from_ban(g, ban_ns, hn_id, hn_label, hn_geom, th_id, th_label, cp_label, arrdt_id, arrdt_label, source_time_description, lang):
    # URIs des entités géographiques de la BAN
    hn_uri, hn_type_uri = gr.generate_uri(np.FACTOIDS, "HN"), np.LTYPE["HouseNumber"]
    th_uri, th_type_uri = gr.generate_uri(np.FACTOIDS, "TH"), np.LTYPE["Thoroughfare"]
    cp_uri, cp_type_uri = gr.generate_uri(np.FACTOIDS, "CP"), np.LTYPE["PostalCodeArea"]
    arrdt_uri, arrdt_type_uri = gr.generate_uri(np.FACTOIDS, "ARRDT"), np.LTYPE["District"]

    # Création des sources
    prov_hn_uri = ban_ns[hn_id]
    prov_th_uri = ban_ns[th_id]
    prov_arrdt_uri = ban_ns[arrdt_id]

    prov_uris = [prov_hn_uri, prov_th_uri, prov_arrdt_uri]
    for uri in prov_uris:
        gr.create_prov_entity(g, uri)

    # URIs pour l'adresse et ses segments
    addr_uri = gr.generate_uri(np.FACTOIDS, "ADDR")
    addr_seg_1_uri = gr.generate_uri(np.FACTOIDS, "AS")
    addr_seg_2_uri = gr.generate_uri(np.FACTOIDS, "AS")
    addr_seg_3_uri = gr.generate_uri(np.FACTOIDS, "AS")
    addr_seg_4_uri = gr.generate_uri(np.FACTOIDS, "AS")

    addr_label = f"{hn_label} {th_label}, {cp_label} {arrdt_label}"

    # Création du numéro de voie (HouseNumber)
    hn_name_attr_version_value = gr.get_name_literal(hn_label, None)
    hn_geom_attr_version_value = gr.get_geometry_wkt_literal(hn_geom)
    hn_attr_types_and_values = [[np.ATYPE["Name"], hn_name_attr_version_value], [np.ATYPE["Geometry"], hn_geom_attr_version_value]]
    msp.create_landmark_version(g, hn_uri, hn_type_uri, hn_label, hn_attr_types_and_values, source_time_description, prov_hn_uri, np.FACTOIDS, None)

    # Création de la voie (Thorhoughfare)
    th_name_attr_version_value = gr.get_name_literal(th_label, lang)
    th_attr_types_and_values = [[np.ATYPE["Name"], th_name_attr_version_value]]
    msp.create_landmark_version(g, th_uri, th_type_uri, th_label, th_attr_types_and_values, source_time_description, prov_th_uri, np.FACTOIDS, lang)

    # Création de la zone du code postal (PostalCodeArea)
    cp_name_attr_version_value = gr.get_name_literal(cp_label, None)
    cp_attr_types_and_values = [[np.ATYPE["Name"], cp_name_attr_version_value]]
    msp.create_landmark_version(g, cp_uri, cp_type_uri, cp_label, cp_attr_types_and_values, source_time_description, prov_hn_uri, np.FACTOIDS, None)

    # Création de l'arrondissement (District)
    arrdt_name_attr_version_value = gr.get_name_literal(arrdt_label, lang)
    arrdt_insee_attr_version_value = gr.get_name_literal(arrdt_id, None)
    arrdt_attr_types_and_values = [[np.ATYPE["Name"], arrdt_name_attr_version_value], [np.ATYPE["InseeCode"], arrdt_insee_attr_version_value]]
    msp.create_landmark_version(g, arrdt_uri, arrdt_type_uri, arrdt_label, arrdt_attr_types_and_values, source_time_description, prov_arrdt_uri, np.FACTOIDS, lang)

    # Création de l'adresse (avec les segments d'adresse)
    gr.create_landmark_relation(g, addr_seg_1_uri, hn_uri, [hn_uri], np.LRTYPE["IsSimilarTo"], is_address_segment=True)
    gr.create_landmark_relation(g, addr_seg_2_uri, hn_uri, [th_uri], np.LRTYPE["Belongs"], is_address_segment=True)
    gr.create_landmark_relation(g, addr_seg_3_uri, hn_uri, [cp_uri], np.LRTYPE["Within"], is_address_segment=True)
    gr.create_landmark_relation(g, addr_seg_4_uri, hn_uri, [arrdt_uri], np.LRTYPE["Within"], is_final_address_segment=True)
    gr.create_address(g, addr_uri, addr_label, lang, [addr_seg_1_uri, addr_seg_2_uri, addr_seg_3_uri, addr_seg_4_uri], hn_uri)

    # Ajout des sources
    uris = [addr_uri, addr_seg_1_uri, addr_seg_2_uri, addr_seg_3_uri, addr_seg_4_uri]
    for uri in uris:
        gr.add_provenance_to_resource(g, uri, prov_hn_uri)

## Données d'OSM
def create_factoids_repository_osm(graphdb_url, osm_repository_name, tmp_folder,
                          ont_file, ontology_named_graph_name,
                          factoids_named_graph_name, permanent_named_graph_name,
                          osm_csv_file, osm_hn_csv_file, osm_kg_file, osm_time_description={}, lang=None):

    # Création d'un graphe basique avec rdflib et export dans le fichier `osm_kg_file`
    g = create_graph_from_osm(osm_csv_file, osm_hn_csv_file, osm_time_description, lang)

    # Export du graphe et import de ce dernier dans le répertoire
    msp.transfert_rdflib_graph_to_factoids_repository(graphdb_url, osm_repository_name, factoids_named_graph_name, g, osm_kg_file, tmp_folder, ont_file, ontology_named_graph_name)

    # Adaptation des données avec l'ontologie, fusion de doublons...
    clean_repository_osm(graphdb_url, osm_repository_name, factoids_named_graph_name, permanent_named_graph_name, lang)

def create_graph_from_osm(osm_file, osm_hn_file, osm_time_description:dict, lang:str):
    osm_pref, osm_ns = "osm", Namespace("http://www.openstreetmap.org/")
    osm_rel_pref, osm_rel_ns = "osmRel", Namespace("http://www.openstreetmap.org/relation/")

    ## Colonnes du fichier OSM
    hn_id_col, hn_number_col, hn_geom_col = "houseNumberId", "houseNumberLabel", "houseNumberGeomWKT"
    th_id_col, th_name_col = "streetId",  "streetName"
    arrdt_id_col, arrdt_name_col, arrdt_insee_col = "arrdtId", "arrdtName", "arrdtInsee"

    # Lecture des deux fichiers
    content = fm.read_csv_file_as_dict(osm_file, id_col=hn_id_col, delimiter=",", encoding='utf-8-sig')
    content_hn = fm.read_csv_file_as_dict(osm_hn_file, id_col=hn_id_col, delimiter=",", encoding='utf-8-sig')

    g = Graph()
    gr.add_namespaces_to_graph(g, np.namespaces_with_prefixes)
    g.bind(osm_pref, osm_ns)
    g.bind(osm_rel_pref, osm_rel_ns)

    osm_time_description = tp.get_valid_time_description(osm_time_description)

    for value in content.values():

        hn_id = value.get(hn_id_col)
        try:
            hn_label = content_hn.get(hn_id).get(hn_number_col)
        except:
            hn_label = None

        try:
            hn_geom = content_hn.get(hn_id).get(hn_geom_col)
        except:
            hn_geom = None

        th_label = value.get(th_name_col)
        th_id = value.get(th_id_col)
        arrdt_id = value.get(arrdt_id_col)
        arrdt_label = value.get(arrdt_name_col)
        arrdt_insee = value.get(arrdt_insee_col)
        create_data_value_from_osm(g, hn_id, hn_label, hn_geom, th_id, th_label, arrdt_id, arrdt_label, arrdt_insee, osm_time_description, lang)

    return g

def create_data_value_from_osm(g, hn_id, hn_label, hn_geom, th_id, th_label, arrdt_id, arrdt_label, arrdt_insee, source_time_description, lang):

    # URIs des entités géographiques d'OSM
    hn_uri, hn_type_uri = gr.generate_uri(np.FACTOIDS, "HN"), np.LTYPE["HouseNumber"]
    th_uri, th_type_uri = gr.generate_uri(np.FACTOIDS, "TH"), np.LTYPE["Thoroughfare"]
    arrdt_uri, arrdt_type_uri = gr.generate_uri(np.FACTOIDS, "ARRDT"), np.LTYPE["District"]

    # URIs pour les relations entre repères
    lm_1_uri = gr.generate_uri(np.FACTOIDS, "LR")
    lm_2_uri = gr.generate_uri(np.FACTOIDS, "LR")

    # Création des sources
    prov_hn_uri = URIRef(hn_id)
    prov_th_uri = URIRef(th_id)
    prov_arrdt_uri = URIRef(arrdt_id)

    prov_uris = [prov_hn_uri, prov_th_uri, prov_arrdt_uri]
    for uri in prov_uris:
        gr.create_prov_entity(g, uri)

    # Création du numéro de voie (HouseNumber)
    hn_name_attr_version_value = gr.get_name_literal(hn_label, None)
    hn_geom_attr_version_value = gr.get_geometry_wkt_literal(hn_geom)
    hn_attr_types_and_values = [[np.ATYPE["Name"], hn_name_attr_version_value], [np.ATYPE["Geometry"], hn_geom_attr_version_value]]
    msp.create_landmark_version(g, hn_uri, hn_type_uri, hn_label, hn_attr_types_and_values, source_time_description, prov_hn_uri, np.FACTOIDS, None)

    # Création de la voie (Thorhoughfare)
    th_name_attr_version_value = gr.get_name_literal(th_label, lang)
    th_attr_types_and_values = [[np.ATYPE["Name"], th_name_attr_version_value]]
    msp.create_landmark_version(g, th_uri, th_type_uri, th_label, th_attr_types_and_values, source_time_description, prov_th_uri, np.FACTOIDS, lang)

    # Création de l'arrondissement (District)
    arrdt_name_attr_version_value = gr.get_name_literal(arrdt_label, lang)
    arrdt_insee_attr_version_value = gr.get_name_literal(arrdt_insee, None)
    arrdt_attr_types_and_values = [[np.ATYPE["Name"], arrdt_name_attr_version_value], [np.ATYPE["InseeCode"], arrdt_insee_attr_version_value]]
    msp.create_landmark_version(g, arrdt_uri, arrdt_type_uri, arrdt_label, arrdt_attr_types_and_values, source_time_description, prov_arrdt_uri, np.FACTOIDS, lang)

    # Création des relations entre repères
    gr.create_landmark_relation(g, lm_1_uri, hn_uri, [th_uri], np.LRTYPE["Belongs"])
    gr.create_landmark_relation(g, lm_2_uri, hn_uri, [arrdt_uri], np.LRTYPE["Within"])

    # Ajout des sources aux relations entre repères
    gr.add_provenance_to_resource(g, lm_1_uri, prov_th_uri)
    gr.add_provenance_to_resource(g, lm_2_uri, prov_arrdt_uri)


def clean_repository_osm(graphdb_url, repository_name, factoids_named_graph_name, permanent_named_graph_name, lang):
    factoids_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, factoids_named_graph_name)
    permanent_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, permanent_named_graph_name)

    # Détection des arrondissements et quartiers qui ont un hiddenLabel similaire
    # Faire de même avec les codes postaux et les voies
    landmark_types = [np.LTYPE["District"], np.LTYPE["PostalCodeArea"], np.LTYPE["Thoroughfare"]]
    for ltype in landmark_types:
        msp.merge_similar_landmarks_with_hidden_labels(graphdb_url, repository_name, ltype, factoids_named_graph_uri)

    landmark_types = [np.LTYPE["HouseNumber"], np.LTYPE["DistrictNumber"], np.LTYPE["StreetNumber"]]
    for ltype in landmark_types:
        lrtype = np.LRTYPE["Belongs"]
        msp.merge_similar_landmarks_with_hidden_label_and_landmark_relation(graphdb_url, repository_name, ltype, lrtype, factoids_named_graph_uri)

    msp.merge_similar_landmark_relations(graphdb_url, repository_name, factoids_named_graph_uri)
    msp.detect_similar_time_interval_of_landmarks(graphdb_url, repository_name, np.SKOS["exactMatch"], factoids_named_graph_uri)

    # Transférer toutes les descriptions de provenance vers le graphe nommé permanent
    msp.transfert_immutable_triples(graphdb_url, repository_name, factoids_named_graph_uri, permanent_named_graph_uri)

    # L'URI ci-dessous définit la source liée à la ville de Paris
    vdp_source_uri = np.FACTS["Source_OSM"]
    source_label = "OpenStreetMap"
    source_lang = "mul"
    msp.create_source_resource(graphdb_url, repository_name, vdp_source_uri, source_label, None, source_lang, np.FACTS, permanent_named_graph_uri)
    msp.link_provenances_with_source(graphdb_url, repository_name, vdp_source_uri, permanent_named_graph_uri)

## Données de la ville de Paris

def create_factoids_repository_ville_paris(graphdb_url, vdp_repository_name, tmp_folder,
                                  ont_file, ontology_named_graph_name,
                                  factoids_named_graph_name, permanent_named_graph_name,
                                  vdpa_csv_file, vdpc_csv_file, vdp_kg_file, vdp_time_description={}, lang=None):

    # Création d'un graphe basique avec rdflib et export dans le fichier `vpt_kg_file`
    g = create_graph_from_ville_paris_actuelles(vdpa_csv_file, vdp_time_description, lang)
    g += create_graph_from_ville_paris_caduques(vdpc_csv_file, vdp_time_description, lang)

    # Export du graphe et import de ce dernier dans le répertoire
    msp.transfert_rdflib_graph_to_factoids_repository(graphdb_url, vdp_repository_name, factoids_named_graph_name, g, vdp_kg_file, tmp_folder, ont_file, ontology_named_graph_name)

    # Adaptation des données avec l'ontologie, fusion de doublons...
    clean_repository_ville_paris(graphdb_url, vdp_repository_name, factoids_named_graph_name, permanent_named_graph_name, lang)


def create_graph_from_ville_paris_caduques(vpc_file, source_time_description, lang:str):
    vpc_pref, vpc_ns = "vdpc", Namespace("https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/denominations-des-voies-caduques/records/")

    # Colonnes du fichier
    id_col = "Identifiant"
    name_col = "Dénomination complète minuscule"
    start_time_col = "Date de l'arrêté"
    end_time_col = "Date de caducité"
    arrdt_col = "Arrondissement"
    district_col = "Quartier"

    vpc_content = fm.read_csv_file_as_dict(vpc_file, id_col=id_col, delimiter=";", encoding='utf-8-sig')
    g = Graph()
    gr.add_namespaces_to_graph(g, np.namespaces_with_prefixes)
    g.bind(vpc_pref, vpc_ns)

    for value in vpc_content.values():
        th_id = value.get(id_col)
        th_label = value.get(name_col)
        th_start_time = value.get(start_time_col)
        th_end_time = value.get(end_time_col)
        th_arrdt_names = sp.split_cell_content(value.get(arrdt_col), sep=",")
        th_district_names = sp.split_cell_content(value.get(district_col), sep=",")

        create_data_value_from_ville_paris_caduques(g, th_id, th_label, th_start_time, th_end_time, th_arrdt_names, th_district_names, source_time_description, vpc_ns, lang)

    return g

def create_landmark_change_and_event(g, lm_label, lm_type:URIRef, lm_prov_uri:URIRef, appeareance:bool, time_list:list, lang):
        # Création d'URIs
        lm_label_lit, lm_uri = Literal(lm_label, lang=lang), gr.generate_uri(np.FACTOIDS, "LM")
        name_attr_uri, name_attr_type_uri, name_attr_version_uri = gr.generate_uri(np.FACTOIDS, "ATTR"), np.ATYPE["Name"], gr.generate_uri(np.FACTOIDS, "AV")
        time_uri, event_uri = gr.generate_uri(np.FACTOIDS, "TI"), gr.generate_uri(np.FACTOIDS, "EV")
        lm_change_app_uri, name_attr_change_app_uri = gr.generate_uri(np.FACTOIDS, "CG"), gr.generate_uri(np.FACTOIDS, "CG")
        time_stamp, time_calendar, time_precision = time_list

        # Définition des types de changements en fonction de si on veut une apparition ou pas
        if appeareance:
            lm_change_app_type_uri = np.CTYPE["LandmarkAppearance"]
            name_attr_change_app_type_uri = np.CTYPE["AttributeVersionAppearance"]
            gr.create_attribute_change(g, name_attr_change_app_uri, name_attr_change_app_type_uri, name_attr_uri, made_effective_versions_uris=[name_attr_version_uri])
        else:
            lm_change_app_type_uri = np.CTYPE["LandmarkDisappearance"]
            name_attr_change_app_type_uri = np.CTYPE["AttributeVersionDisappearance"]
            gr.create_attribute_change(g, name_attr_change_app_uri, name_attr_change_app_type_uri, name_attr_uri, outdated_versions_uris=[name_attr_version_uri])

        gr.create_landmark(g, lm_uri, lm_label, lang, lm_type)
        gr.create_landmark_attribute_and_version(g, lm_uri, name_attr_uri, name_attr_type_uri, name_attr_version_uri, lm_label_lit)
        gr.create_landmark_change(g, lm_change_app_uri, lm_change_app_type_uri, lm_uri)
        gr.create_crisp_time_instant(g, time_uri, time_stamp, time_calendar, time_precision)
        gr.create_event_with_time(g, event_uri, time_uri)
        gr.create_change_event_relation(g, lm_change_app_uri, event_uri)
        gr.create_change_event_relation(g, name_attr_change_app_uri, event_uri)

        uris = [event_uri, lm_uri, name_attr_version_uri]
        for uri in uris:
            gr.add_provenance_to_resource(g, uri, lm_prov_uri)

def create_data_value_from_ville_paris_caduques(g:Graph, th_id:str, th_label:str, start_time_stamp:str, end_time_stamp:str, arrdt_labels:list[str], district_labels:list[str], source_time_description, vpa_ns:Namespace, lang:str):
    """
    `source_time_description` : dictionnaire décrivant les dates de début et de fin de validité de la source
    `source_time_description = {"start_time":{"stamp":..., "precision":..., "calendar":...}, "end_time":{} }`
    """


    # URI de la voie, création de cette dernière, ajout d'une géométrie et de labels alternatifs
    th_uri, th_type_uri = gr.generate_uri(np.FACTOIDS, "TH"), np.LTYPE["Thoroughfare"]
    name_attr_uri, name_attr_type_uri, name_attr_version_uri = gr.generate_uri(np.FACTOIDS, "ATTR"), np.ATYPE["Name"], gr.generate_uri(np.FACTOIDS, "AV")
    name_attr_version_value = gr.get_name_literal(th_label, lang)

    gr.create_landmark(g, th_uri, th_label, lang, th_type_uri)
    gr.create_landmark_attribute_and_version(g, th_uri, name_attr_uri, name_attr_type_uri, name_attr_version_uri, name_attr_version_value)
    # msp.add_other_labels_for_resource(g, th_uri, th_label, lang, th_type_uri)
    msp.add_validity_time_interval_to_landmark(g, th_uri, source_time_description)

    # Création de la provenance
    th_prov_uri = vpa_ns[th_id]
    gr.create_prov_entity(g, th_prov_uri)
    gr.add_provenance_to_resource(g, th_uri, th_prov_uri)
    gr.add_provenance_to_resource(g, name_attr_version_uri, th_prov_uri)

    start_time_stamp, start_time_calendar, start_time_precision = tp.get_gregorian_date_from_timestamp(start_time_stamp)
    end_time_stamp, end_time_calendar, end_time_precision = tp.get_gregorian_date_from_timestamp(end_time_stamp)

    # Ajout d'un événement qui décrit l'apparition de la voie et de son nom (si une date l'indique)
    if start_time_stamp is not None:
        create_landmark_change_and_event(g, th_label, th_type_uri, th_prov_uri, True, [start_time_stamp, start_time_calendar, start_time_precision], lang)

    # Ajout d'un événement qui décrit la disparition de la voie et de son nom (si une date l'indique)
    if end_time_stamp is not None:
        create_landmark_change_and_event(g, th_label, th_type_uri, th_prov_uri, False, [end_time_stamp, end_time_calendar, end_time_precision], lang)

    # Liste des zones à créer (arrondissement et quartier), chaque élément est une liste dont la 1re valeur est le label et la seconde est son type
    # Exemple : areas = [["3e arrondissement de Paris", "District"], ["Maison Blanche", "District"]]
    areas = [[re.sub("^0", "", x.replace("01e", "01er")) + " arrondissement de Paris", "District"] for x in arrdt_labels] + [[x, "District"] for x in district_labels]
    for area in areas:
        area_label, area_type = area
        create_area_location_of_landmark(g, area_label, area_type, th_uri, th_prov_uri, source_time_description, lang)

def create_graph_from_ville_paris_actuelles(vpa_file, source_time_description, lang:str):
    vpa_pref, vpa_ns = "vdpa", Namespace("https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/denominations-emprises-voies-actuelles/records/")

    # Colonnes du fichier
    id_col = "Identifiant"
    name_col = "Dénomination complète minuscule"
    start_time_col = "Date de l'arrété"
    arrdt_col = "Arrondissement"
    district_col = "Quartier"
    geom_col = "geo_shape"

    content = fm.read_csv_file_as_dict(vpa_file, id_col=id_col, delimiter=";", encoding='utf-8-sig')
    g = Graph()
    gr.add_namespaces_to_graph(g, np.namespaces_with_prefixes)
    g.bind(vpa_pref, vpa_ns)

    source_time_description = tp.get_valid_time_description(source_time_description)

    for value in content.values():
        th_id = value.get(id_col)
        th_label = value.get(name_col)
        th_geom = value.get(geom_col)
        th_start_time = value.get(start_time_col)
        th_arrdt_labels = sp.split_cell_content(value.get(arrdt_col), sep=",")
        th_district_labels = sp.split_cell_content(value.get(district_col), sep=",")

        create_data_value_from_ville_paris_actuelles(g, th_id, th_label, th_geom, th_start_time, th_arrdt_labels, th_district_labels, source_time_description, vpa_ns, lang)

    return g


def get_attr_uri_and_attr_version_uri(g:Graph, lm_uri:URIRef, attr_type_uri:URIRef):
    for lm_uri, pred, attr_uri in g.triples((lm_uri, np.ADDR["hasAttribute"], None)):
        if g.value(attr_uri, np.ADDR["isAttributeType"]) == attr_type_uri:
            attr_version_uri = g.value(attr_uri, np.ADDR["hasAttributeVersion"])
            return [attr_uri, attr_version_uri]
    return [None, None]

def create_data_value_from_ville_paris_actuelles(g:Graph, th_id:str, th_label:str, th_geom:str, start_time_stamp:str, arrdt_labels:list[str], district_labels:list[str], source_time_description, vpa_ns:Namespace, lang:str):
    """
    `source_time_description` : dictionnaire décrivant les dates de début et de fin de validité de la source
    `source_time_description = {"start_time":{"stamp":..., "precision":..., "calendar":...}, "end_time":{} }`
    """

    # Conversion de la geométrie (qui est un geojson en string) vers un WKT
    wkt_geom = gp.from_geojson_to_wkt(json.loads(th_geom))
    geom_attr_version_value = gr.get_geometry_wkt_literal(wkt_geom)
    name_attr_version_value = gr.get_name_literal(th_label, lang)

    # URI de la voie, création de cette dernière, ajout d'une géométrie et de labels alternatifs
    th_uri, th_type_uri = gr.generate_uri(np.FACTOIDS, "TH"), np.LTYPE["Thoroughfare"]

    # Création de la provenance
    th_prov_uri = vpa_ns[th_id]
    gr.create_prov_entity(g, th_prov_uri)

    th_attr_types_and_values = [[np.ATYPE["Name"], name_attr_version_value], [np.ATYPE["Geometry"], geom_attr_version_value]]
    msp.create_landmark_version(g, th_uri, th_type_uri, th_label, th_attr_types_and_values, source_time_description, th_prov_uri, np.FACTOIDS, lang)

    start_time_stamp, start_time_calendar, start_time_precision = tp.get_gregorian_date_from_timestamp(start_time_stamp)

    # Liste des zones à créer (arrondissement et quartier), chaque élément est une liste dont la 1re valeur est le label et la seconde est son type
    # Exemple : areas = [["3e arrondissement de Paris", "District"], ["Maison Blanche", "District"]]
    areas = [[re.sub("^0", "", x.replace("01e", "01er")) + " arrondissement de Paris", "District"] for x in arrdt_labels] + [[x, "District"] for x in district_labels]
    for area in areas:
        area_label, area_type = area
        create_area_location_of_landmark(g, area_label, area_type, th_uri, th_prov_uri, source_time_description, lang)

    # Ajout d'un événement qui décrit l'apparition de la voie et de son nom (si une date l'indique)
    if start_time_stamp is not None:
        create_landmark_change_and_event(g, th_label, th_type_uri, th_prov_uri, True, [start_time_stamp, start_time_calendar, start_time_precision], lang)

def create_area_location_of_landmark(g, area_label, area_type, lm_uri, lm_prov_uri, source_time_description, lang):
        """
        Création d'une zone dont le landmark défini par `lm_uri` est situé à l'intérieur
        """

        area_type_uri = np.LTYPE[area_type]

        # URI de la zone et de la relation entre la voie et la zone
        area_uri, lr_uri = gr.generate_uri(np.FACTOIDS, "LM"), gr.generate_uri(np.FACTOIDS, "LR")

        # URIs des ressources liée à un attribut de type nom
        name_attr_area_uri, name_attr_type_area_uri, name_attr_version_area_uri = gr.generate_uri(np.FACTOIDS, "ATTR"), np.ATYPE["Name"], gr.generate_uri(np.FACTOIDS, "AV")
        name_attr_version_area_value = gr.get_name_literal(area_label, lang)

        gr.create_landmark(g, area_uri, area_label, lang, area_type_uri)
        gr.create_landmark_attribute_and_version(g, area_uri, name_attr_area_uri, name_attr_type_area_uri, name_attr_version_area_uri, name_attr_version_area_value)
        gr.create_landmark_relation(g, lr_uri, lm_uri, [area_uri], np.LRTYPE["Within"])
        msp.add_other_labels_for_resource(g, area_uri, area_label, lang, area_type_uri)
        msp.add_other_labels_for_resource(g, name_attr_version_area_uri, area_label, lang, area_type_uri)
        msp.add_validity_time_interval_to_landmark(g, area_uri, source_time_description)

        # Ajout des provenances
        uris = [area_uri, lr_uri, name_attr_version_area_uri]
        for uri in uris:
            gr.add_provenance_to_resource(g, uri, lm_prov_uri)

def clean_repository_ville_paris(graphdb_url:str, repository_name:str, factoids_named_graph_name:str, permanent_named_graph_name:str, lang:str):
    factoids_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, factoids_named_graph_name)
    permanent_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, permanent_named_graph_name)

    # Fusion des repères similaires (s'applique uniquement aux quartiers et arrondissements)
    landmark_types = [np.LTYPE["District"], np.LTYPE["PostalCodeArea"], np.LTYPE["Thoroughfare"]]
    for landmark_type in landmark_types:
        msp.merge_similar_landmark_versions_with_hidden_labels(graphdb_url, repository_name, landmark_type, factoids_named_graph_uri)
    msp.merge_similar_landmark_relations(graphdb_url, repository_name, factoids_named_graph_uri)
    msp.detect_similar_time_interval_of_landmarks(graphdb_url, repository_name, np.SKOS["exactMatch"], factoids_named_graph_uri)

    # Transférer toutes les descriptions de provenance vers le graphe nommé permanent
    msp.transfert_immutable_triples(graphdb_url, repository_name, factoids_named_graph_uri, permanent_named_graph_uri)

    # L'URI ci-dessous définit la source liée à la ville de Paris
    vdp_source_uri = np.FACTS["Source_VDP"]
    source_label = "dénomination des voies de Paris (actuelles et caduques)"
    publisher_label = "Département de la Topographie et de la Documentation Foncière de la Ville de Paris"
    msp.create_source_resource(graphdb_url, repository_name, vdp_source_uri, source_label, publisher_label, lang, np.FACTS, permanent_named_graph_uri)
    msp.link_provenances_with_source(graphdb_url, repository_name, vdp_source_uri, permanent_named_graph_uri)

## Données de Wikidata

def get_paris_landmarks_from_wikidata(out_csv_file):
    """
    Obtention des voies de Paris et des communes de l'ancien département de la Seine
    """

    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX pqv: <http://www.wikidata.org/prop/qualifier/value/>
    PREFIX wb: <http://wikiba.se/ontology#>
    PREFIX time: <http://www.w3.org/2006/time#>

    SELECT DISTINCT ?landmarkId ?landmarkType ?nomOff ?startTimeStamp ?startTimePrec ?startTimeCal ?startTimeDef ?endTimeStamp ?endTimePrec ?endTimeCal ?endTimeDef ?statement ?statementType
    WHERE {
        {
            ?landmarkId p:P361 [ps:P361 wd:Q16024163].
            BIND("Thoroughfare" AS ?landmarkType)
        }UNION{
            ?landmarkId p:P361 [ps:P361 wd:Q107311481].
            BIND("Thoroughfare" AS ?landmarkType)
        }UNION{
            ?landmarkId p:P31 [ps:P31 wd:Q252916].
            BIND("District" AS ?landmarkType)
        }UNION{
            ?landmarkId p:P31 [ps:P31 wd:Q702842]; p:P131 [ps:P131 wd:Q90].
            BIND("District" AS ?landmarkType)
        }UNION{
            ?landmarkId p:P31 [ps:P31 wd:Q484170]; p:P131 [ps:P131 wd:Q1142326].
            BIND("City" AS ?landmarkType)
        }
        {
            ?landmarkId p:P1448 ?nomOffSt.
            ?nomOffSt ps:P1448 ?nomOff.
            BIND(?nomOffSt AS ?statement)
            BIND(wb:Statement AS ?statementType)
            OPTIONAL {?nomOffSt pqv:P580 ?startTimeValSt }
            OPTIONAL {?nomOffSt pqv:P582 ?endTimeValSt }
        }UNION{
            ?landmarkId rdfs:label ?nomOff.
            FILTER (LANG(?nomOff) = "fr")
            MINUS {?landmarkId p:P1448 ?nomOffSt}
            BIND(?landmarkId AS ?statement)
            BIND(wb:Item AS ?statementType)
        }
        OPTIONAL { ?landmarkId p:P571 [psv:P571 ?startTimeValIt] }
        OPTIONAL { ?landmarkId p:P576 [psv:P576 ?endTimeValIt] }
        BIND(IF(BOUND(?startTimeValSt), ?startTimeValSt, IF(BOUND(?startTimeValIt), ?startTimeValIt, "")) AS ?startTimeVal)
        BIND(IF(BOUND(?endTimeValSt), ?endTimeValSt, IF(BOUND(?endTimeValIt), ?endTimeValIt, "")) AS ?endTimeVal)
        OPTIONAL { ?startTimeVal wb:timeValue ?startTimeStamp ; wb:timePrecision ?startTimePrecRaw ; wb:timeCalendarModel ?startTimeCal . }
        OPTIONAL { ?endTimeVal wb:timeValue ?endTimeStamp ; wb:timePrecision ?endTimePrecRaw ; wb:timeCalendarModel ?endTimeCal . }
        BIND(IF(?statementType = wb:Statement, BOUND(?startTimeValSt), IF(?statementType = wb:Item, BOUND(?startTimeValIt), "false"^^xsd:boolean)) AS ?startTimeDef)
        BIND(IF(?statementType = wb:Statement, BOUND(?endTimeValSt), IF(?statementType = wb:Item, BOUND(?endTimeValIt), "false"^^xsd:boolean)) AS ?endTimeDef)

        BIND(IF(?startTimePrecRaw = 11, time:unitDay,
                IF(?startTimePrecRaw = 10, time:unitMonth,
                    IF(?startTimePrecRaw = 9, time:unitYear,
                        IF(?startTimePrecRaw = 8, time:unitDecade,
                        IF(?startTimePrecRaw = 7, time:unitCentury,
                            IF(?startTimePrecRaw = 6, time:unitMillenium, ?x
                                )))))) AS ?startTimePrec)
        BIND(IF(?endTimePrecRaw = 11, time:unitDay,
                IF(?endTimePrecRaw = 10, time:unitMonth,
                    IF(?endTimePrecRaw = 9, time:unitYear,
                        IF(?endTimePrecRaw = 8, time:unitDecade,
                        IF(?endTimePrecRaw = 7, time:unitCentury,
                            IF(?endTimePrecRaw = 6, time:unitMillenium, ?x
                                )))))) AS ?endTimePrec)
        }
    """

    query = wd.save_select_query_as_csv_file(query, out_csv_file)


def get_paris_locations_from_wikidata(out_csv_file):
    """
    Obtenir la localisation des données (voies et zones) de Paris depuis Wikidata"""

    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX pqv: <http://www.wikidata.org/prop/qualifier/value/>
    PREFIX wb: <http://wikiba.se/ontology#>
    PREFIX time: <http://www.w3.org/2006/time#>

    SELECT DISTINCT ?locatumId ?relatumId ?landmarkRelationType ?dateStartStamp ?dateStartCal ?dateStartPrec ?dateEndStamp ?dateEndCal ?dateEndPrec ?statement ?statementType WHERE {
    {
        ?locatumId p:P361 [ps:P361 wd:Q16024163].
    }UNION{
        ?locatumId p:P361 [ps:P361 wd:Q107311481].
    }UNION{
        ?locatumId p:P31 [ps:P31 wd:Q252916].
    }UNION{
        ?locatumId p:P31 [ps:P31 wd:Q702842]; p:P131 [ps:P131 wd:Q90].
    }UNION{
        ?locatumId p:P31 [ps:P31 wd:Q484170]; p:P131 [ps:P131 wd:Q1142326].
    }
    BIND(wb:Statement AS ?statementType)
    ?locatumId p:P131 ?statement.
    ?statement ps:P131 ?relatumId.
    OPTIONAL {?statement pq:P580 ?dateStartStamp; pqv:P580 [wb:timeCalendarModel ?dateStartCal ; wb:timePrecision ?dateStartPrecRaw]}
    OPTIONAL {?statement pq:P582 ?dateEndStamp; pqv:P582 [wb:timeCalendarModel ?dateEndCal; wb:timePrecision ?dateEndPrecRaw]}
    BIND("Within" AS ?landmarkRelationType)
    BIND(IF(?dateStartPrecRaw = 11, time:unitDay,
            IF(?dateStartPrecRaw = 10, time:unitMonth,
                IF(?dateStartPrecRaw = 9, time:unitYear,
                    IF(?dateStartPrecRaw = 8, time:unitDecade,
                    IF(?dateStartPrecRaw = 7, time:unitCentury,
                        IF(?dateStartPrecRaw = 6, time:unitMillenium, ?x
                            )))))) AS ?dateStartPrec)
    BIND(IF(?dateEndPrecRaw = 11, time:unitDay,
            IF(?dateEndPrecRaw = 10, time:unitMonth,
                IF(?dateEndPrecRaw = 9, time:unitYear,
                    IF(?dateEndPrecRaw = 8, time:unitDecade,
                    IF(?dateEndPrecRaw = 7, time:unitCentury,
                        IF(?dateEndPrecRaw = 6, time:unitMillenium, ?x
                            )))))) AS ?dateEndPrec)
    }
    """

    query = wd.save_select_query_as_csv_file(query, out_csv_file)

## Faire appel aux endpoint de Wikidata pour sélectionner des données
def get_data_from_wikidata(wdp_land_csv_file, wdp_loc_csv_file):
    """
    Obtenir les fichiers CSV pour les données provenant de Wikidata
    """
    get_paris_landmarks_from_wikidata(wdp_land_csv_file)
    get_paris_locations_from_wikidata(wdp_loc_csv_file)

def create_factoids_repository_wikidata_paris(graphdb_url, wdp_repository_name, tmp_folder,
                                     ont_file, ontology_named_graph_name,
                                     factoids_named_graph_name, permanent_named_graph_name,
                                     wdp_land_csv_file, wdp_loc_csv_file, wdp_kg_file, wdp_time_description={}, lang=None):

    # Création d'un graphe basique avec rdflib et export dans le fichier `wdp_kg_file`
    g = create_graph_from_wikidata_paris(wdp_land_csv_file, wdp_loc_csv_file, wdp_time_description, lang)

    # Export du graphe et import de ce dernier dans le répertoire
    msp.transfert_rdflib_graph_to_factoids_repository(graphdb_url, wdp_repository_name, factoids_named_graph_name, g, wdp_kg_file, tmp_folder, ont_file, ontology_named_graph_name)

    # Adaptation des données avec l'ontologie, fusion de doublons...
    clean_repository_wikidata_paris(graphdb_url, wdp_repository_name, wdp_time_description, factoids_named_graph_name, permanent_named_graph_name, lang)

def create_graph_from_wikidata_paris(wdp_land_file, wdp_loc_file, source_time_description, lang):
    wd_pref, wd_ns = "wd", Namespace("http://www.wikidata.org/entity/")
    wds_pref, wds_ns = "wds", Namespace("http://www.wikidata.org/entity/statement/")
    wb_pref, wb_ns = "wb", Namespace("http://wikiba.se/ontology#")
    wiki_prefixes_and_namespaces = [[wd_pref, wd_ns], [wds_pref, wds_ns], [wb_pref, wb_ns]]

    ## Colonnes du fichier Wikidata
    lm_id_col, lm_type_col, lm_label_col = "landmarkId", "landmarkType", "nomOff"
    prov_id_col, prov_id_type_col = "statement", "statementType"
    lr_type_col = "landmarkRelationType"
    locatum_id_col, relatum_id_col = "locatumId","relatumId"
    start_time_stamp_col, start_time_cal_col, start_time_prec_col, start_time_def_col = "startTimeStamp", "startTimeCal", "startTimePrec", "startTimeDef"
    end_time_stamp_col, end_time_cal_col, end_time_prec_col, end_time_def_col = "endTimeStamp", "endTimeCal", "endTimePrec", "endTimeDef"

    # Lecture des deux fichiers
    content_lm = fm.read_csv_file_as_dict(wdp_land_file, id_col=lm_id_col, delimiter=",", encoding='utf-8-sig')
    content_lr = fm.read_csv_file_as_dict(wdp_loc_file, delimiter=",", encoding='utf-8-sig')

    source_time_description = tp.get_valid_time_description(source_time_description)

    g = Graph()
    gr.add_namespaces_to_graph(g, np.namespaces_with_prefixes)
    for [prefix, ns] in wiki_prefixes_and_namespaces:
        g.bind(prefix, ns)

    # Création des landmarks
    for value in content_lm.values():
        lm_id = value.get(lm_id_col)
        lm_label = value.get(lm_label_col)
        lm_type = value.get(lm_type_col)
        lm_prov_id = value.get(prov_id_col)
        lm_prov_id_type = value.get(prov_id_type_col)
        start_time_stamp = tp.get_literal_time_stamp(value.get(start_time_stamp_col)) if value.get(start_time_stamp_col) != "" else None
        start_time_prec = gr.get_valid_uri(value.get(start_time_prec_col))
        start_time_cal = gr.get_valid_uri(value.get(start_time_cal_col))
        start_time_def = Literal(value.get(start_time_def_col), datatype=XSD.boolean)
        start_time = [start_time_stamp, start_time_cal, start_time_prec, start_time_def]
        end_time_stamp = tp.get_literal_time_stamp(value.get(end_time_stamp_col)) if value.get(end_time_stamp_col) != "" else None
        end_time_prec = gr.get_valid_uri(value.get(end_time_prec_col))
        end_time_cal = gr.get_valid_uri(value.get(end_time_cal_col))
        end_time_def = Literal(value.get(end_time_def_col), datatype=XSD.boolean)
        end_time = [end_time_stamp, end_time_cal, end_time_prec, end_time_def]

        create_data_value_from_wikidata_landmark(g, lm_id, lm_label, lm_type, lm_prov_id, lm_prov_id_type, start_time, end_time, source_time_description, lang)

    # Création des relations entre landmarks
    for value in content_lr.values():
        lr_type = value.get(lr_type_col)
        lr_prov_id = value.get(prov_id_col)
        lr_prov_id_type = value.get(prov_id_type_col)
        locatum_id = value.get(locatum_id_col)
        relatum_id = value.get(relatum_id_col)
        create_data_value_from_wikidata_landmark_relation(g, lr_type, locatum_id, relatum_id, lr_prov_id, lr_prov_id_type)

    return g

def create_data_value_from_wikidata_landmark(g, lm_id, lm_label, lm_type, lm_prov_id, lm_prov_id_type, start_time:list, end_time:list, source_time_description:dict, lang):
    """
    `source_time_description` : dictionnaire décrivant les dates de début et de fin de validité de la source
    `source_time_description = {"start_time":{"stamp":..., "precision":..., "calendar":...}, "end_time":{} }`
    """

    name_attr_version_value = gr.get_name_literal(lm_label, lang)

    # URI de la voie, création de cette dernière, ajout d'une géométrie et de labels alternatifs
    lm_uri, lm_type_uri = gr.generate_uri(np.FACTOIDS, "LM"), np.LTYPE[lm_type]
    wd_uri = URIRef(lm_id)

    # Création de la provenance
    lm_prov_uri, lm_prov_id_type_uri = URIRef(lm_prov_id), URIRef(lm_prov_id_type)
    gr.create_prov_entity(g, lm_prov_uri)
    g.add((lm_prov_uri, RDF.type, lm_prov_id_type_uri)) # Indiquer que `lm_prov_uri` est un statement ou un item Wikibase
    g.add((lm_uri, SKOS.closeMatch, wd_uri))

    lm_attr_types_and_values = [[np.ATYPE["Name"], name_attr_version_value]]
    msp.create_landmark_version(g, lm_uri, lm_type_uri, lm_label, lm_attr_types_and_values, source_time_description, lm_prov_uri, np.FACTOIDS, lang)

    start_time_stamp, start_time_calendar, start_time_precision, start_time_def = start_time
    end_time_stamp, end_time_calendar, end_time_precision, end_time_def = end_time

    # Ajout d'un événement qui décrit l'apparition de la voie et de son nom (si une date l'indique)
    if start_time_def:
        create_landmark_change_and_event(g, lm_label, lm_type_uri, lm_prov_uri, True, [start_time_stamp, start_time_calendar, start_time_precision], lang)
    if end_time_def:
        create_landmark_change_and_event(g, lm_label, lm_type_uri, lm_prov_uri, False, [end_time_stamp, end_time_calendar, end_time_precision], lang)

    # Ajout de labels alternatifs pour les repères
    # msp.add_other_labels_for_landmark(g, lm_uri, lm_label, lang, lm_type_uri)

def create_data_value_from_wikidata_landmark_relation(g, lr_type, locatum_id, relatum_id, lr_prov_id, lr_prov_id_type):
    # URIs de la relation entre repères
    lr_uri = gr.generate_uri(np.FACTOIDS, "LR")
    locatum_uri = URIRef(locatum_id)
    relatum_uri = URIRef(relatum_id)

    # Création de la provenance
    lr_prov_uri, lr_prov_id_type_uri = URIRef(lr_prov_id), URIRef(lr_prov_id_type)
    gr.create_prov_entity(g, lr_prov_uri)
    g.add((lr_prov_uri, RDF.type, lr_prov_id_type_uri))  # Indiquer que `lr_prov_uri` est un statement Wikibase

    # Création de la relation entre repères
    gr.create_landmark_relation(g, lr_uri, locatum_uri, [relatum_uri], np.LRTYPE[lr_type])
    gr.add_provenance_to_resource(g, lr_uri, lr_prov_uri)

def remove_orphan_provenance_entities(graphdb_url:str, repository_name:str):
    """
    Remove all provenance entities which are not related with any statement
    """

    query = np.query_prefixes + f"""
    DELETE {{
        ?wdLr a addr:LandmarkRelation ; addr:isLandmarkRelationType ?lrType ; addr:locatum ?wdLoc ; addr:relatum ?wdRel ; prov:wasDerivedFrom ?prov.
    }}
    WHERE {{
        ?wdLr a addr:LandmarkRelation ; addr:isLandmarkRelationType ?lrType ; addr:locatum ?wdLoc ; addr:relatum ?wdRel ; prov:wasDerivedFrom ?prov.
        OPTIONAL {{
        ?l skos:closeMatch ?wdLoc .
    	?r skos:closeMatch ?wdRel .
    	BIND(URI(CONCAT(STR(URI(factoids:)), "LR_", STRUUID())) AS ?lmRel)
        }}
        BIND(BOUND(?l) && BOUND(?r) AS ?exist)
        BIND(IF(?exist, ?lmRel, ?x) AS ?lr)
        BIND(IF(?exist, ?l, ?x) AS ?loc)
        BIND(IF(?exist, ?r, ?x) AS ?rel)
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def create_landmark_relations_for_wikidata_paris(graphdb_url:str, repository_name:str, factoids_named_graph_uri:URIRef):
    query1 = np.query_prefixes + f"""
    DELETE {{
        ?wdLr a addr:LandmarkRelation ; addr:isLandmarkRelationType ?lrType ; addr:locatum ?wdLoc ; addr:relatum ?wdRel ; prov:wasDerivedFrom ?prov.
    }}
    INSERT {{
        GRAPH ?g {{
            ?lr a addr:LandmarkRelation ; addr:isLandmarkRelationType ?lrType ; addr:locatum ?loc ; addr:relatum ?rel ; prov:wasDerivedFrom ?prov.
        }}
    }}
    WHERE {{
        BIND({factoids_named_graph_uri.n3()} AS ?g)
        ?wdLr a addr:LandmarkRelation ; addr:isLandmarkRelationType ?lrType ; addr:locatum ?wdLoc ; addr:relatum ?wdRel ; prov:wasDerivedFrom ?prov.
        OPTIONAL {{
        ?l skos:closeMatch ?wdLoc .
    	?r skos:closeMatch ?wdRel .
    	BIND(URI(CONCAT(STR(URI(factoids:)), "LR_", STRUUID())) AS ?lmRel)
        }}
        BIND(BOUND(?l) && BOUND(?r) AS ?exist)
        BIND(IF(?exist, ?lmRel, ?x) AS ?lr)
        BIND(IF(?exist, ?l, ?x) AS ?loc)
        BIND(IF(?exist, ?r, ?x) AS ?rel)
    }}
    """

    # Suppression des provenances orphelines
    query2 = np.query_prefixes + f"""
    DELETE {{
        ?s ?p ?prov .
        ?prov ?p ?o .
    }}
    WHERE {{
        BIND({factoids_named_graph_uri.n3()} AS ?g)
        GRAPH ?g {{?prov a prov:Entity}}
        FILTER NOT EXISTS {{?x prov:wasDerivedFrom ?prov}}
        {{?s ?p ?prov}}UNION{{?prov ?p ?o}}
    }}
    """

    queries = [query1, query2]
    for query in queries:
        gd.update_query(query, graphdb_url, repository_name)


def clean_repository_wikidata_paris(graphdb_url:str, repository_name:str, source_time_description:dict, factoids_named_graph_name:str, permanent_named_graph_name:str, lang:str):
    factoids_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, factoids_named_graph_name)
    permanent_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, permanent_named_graph_name)

    create_landmark_relations_for_wikidata_paris(graphdb_url, repository_name, factoids_named_graph_uri)

    # Transférer toutes les descriptions de provenance vers le graphe nommé permanent
    msp.transfert_immutable_triples(graphdb_url, repository_name, factoids_named_graph_uri, permanent_named_graph_uri)

    # L'URI ci-dessous définit la source liée à Wikidata
    vdp_source_uri = np.FACTS["Source_WD"]
    source_label = "Wikidata"
    source_lang = "mul"
    msp.create_source_resource(graphdb_url, repository_name, vdp_source_uri, source_label, None, source_lang, np.FACTS, permanent_named_graph_uri)
    msp.link_provenances_with_source(graphdb_url, repository_name, vdp_source_uri, permanent_named_graph_uri)

##################################################################

# Données venant de fichiers Geojson

def create_factoids_repository_geojson_states(graphdb_url, repository_name, tmp_folder,
                                              ont_file, ontology_named_graph_name,
                                              factoids_named_graph_name, permanent_named_graph_name,
                                              geojson_content, geojson_join_property, kg_file, tmp_kg_file, landmark_type, lang:str=None):

    """
    Fonction pour faire l'ensemble des processus relatifs à la création des factoïdes pour les données issues d'un fichier Geojson décrivant des états d'un territoire
    """

    # Lire le fichier geojson et fusionner les éléments selon `geojson_join_property`. Par exemple, si `geojson_join_property="name"`,
    # la fonction fusionne toutes les features qui ont le même nom.
    geojson_features = gp.merge_geojson_features_from_one_property(geojson_content, geojson_join_property)
    geojson_features = geojson_content
    geojson_time = geojson_content.get("time")
    geojson_source = geojson_content.get("source")

    time_description = tp.get_valid_time_description(geojson_time)

    # À partir du fichier geojson décrivant des repères (qui sont tous du même type), convertir en un graphe de connaissance selon l'ontologie
    g = create_graph_from_geojson_states(geojson_features, landmark_type, lang, time_description)

    # Export du graphe et import de ce dernier dans le répertoire
    msp.transfert_rdflib_graph_to_factoids_repository(graphdb_url, repository_name, factoids_named_graph_name, g, kg_file, tmp_folder, ont_file, ontology_named_graph_name)

    # Mise à jour du répertoire
    clean_repository_geojson_states(graphdb_url, repository_name, geojson_source, factoids_named_graph_name, permanent_named_graph_name, lang, tmp_kg_file)

def create_landmark_from_geojson_feature(feature:dict, landmark_type:str, g:Graph, srs_uri:URIRef=None, lang:str=None, time_description:dict={}):
    label = feature.get("properties").get("name")

    geometry_prefix = ""
    if srs_uri is not None:
        geometry_prefix = srs_uri.n3() + " "

    geometry = geometry_prefix + gp.from_geojson_to_wkt(feature.get("geometry"))

    landmark_uri, landmark_type_uri = gr.generate_uri(np.FACTOIDS, "LM"), np.LTYPE[landmark_type]

    attr_types_and_values = []
    if geometry is not None:
        geom_attr_version_value = gr.get_geometry_wkt_literal(geometry)
        attr_types_and_values.append([np.ATYPE["Geometry"], geom_attr_version_value])
    if label is not None:
        name_attr_version_value = gr.get_name_literal(label, lang)
        attr_types_and_values.append([np.ATYPE["Name"], name_attr_version_value])

    msp.create_landmark_version(g, landmark_uri, landmark_type_uri, label, attr_types_and_values, time_description, None, np.FACTOIDS, lang)


def create_graph_from_geojson_states(feature_collection:dict, landmark_type:str, lang:str=None, time_description:dict={}):
    crs_dict = {
        "EPSG:4326" : URIRef("http://www.opengis.net/def/crs/EPSG/0/4326"),
        "EPSG:2154" : URIRef("http://www.opengis.net/def/crs/EPSG/0/2154"),
        "urn:ogc:def:crs:OGC:1.3:CRS84" : URIRef("http://www.opengis.net/def/crs/EPSG/0/4326"),
        "urn:ogc:def:crs:EPSG::2154" :  URIRef("http://www.opengis.net/def/crs/EPSG/0/2154"),
    }

    features = feature_collection.get("features")
    geojson_crs = feature_collection.get("crs")
    srs_iri = get_srs_iri_from_geojson_feature_collection(geojson_crs, crs_dict)

    g = Graph()

    for feature in features:
        create_landmark_from_geojson_feature(feature, landmark_type, g, srs_iri, lang=lang, time_description=time_description)

    return g

def get_srs_iri_from_geojson_feature_collection(geojson_crs, crs_dict):
    try:
        crs_name = geojson_crs.get("properties").get("name")
        srs_iri = crs_dict.get(crs_name)
        return srs_iri
    except:
        return None

def create_source_geojson_states(graphdb_url, repository_name, source_uri:URIRef, named_graph_uri:URIRef, geojson_source:dict, facts_namespace:Namespace):
    """
    Création de la source relative aux données du fichier Geojson
    """

    lang = geojson_source.get("lang")
    source_label = geojson_source.get("label")
    publisher_label = geojson_source.get("publisher").get("label")
    msp.create_source_resource(graphdb_url, repository_name, source_uri, source_label, publisher_label, lang, facts_namespace, named_graph_uri)

def create_source_provenances_geojson(graphdb_url, repository_name, source_uri:URIRef, source_prov_uri:URIRef, factoids_named_graph_uri:URIRef, permanent_named_graph_uri:URIRef):
    """
    Création des liens de provenances entre la source et les données d'un fichier Geojson
    """

    prefixes = """
    PREFIX : <http://rdf.geohistoricaldata.org/def/address#>
    PREFIX facts: <http://rdf.geohistoricaldata.org/id/address/facts/>
    PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    """

    query = prefixes + f"""
    INSERT {{
        GRAPH {factoids_named_graph_uri.n3()} {{
            ?elem prov:wasDerivedFrom {source_prov_uri.n3()}.
        }}
        GRAPH {permanent_named_graph_uri.n3()} {{
            {source_prov_uri.n3()} a prov:Entity; rico:isOrWasDescribedBy {source_uri.n3()}.
        }}
    }}
    WHERE {{
        ?elem a ?elemType.
        FILTER(?elemType IN (:Landmark, :LandmarkRelation, :AttributeVersion, :Change, :Event, :TemporalEntity))
    }}
    """

    gd.update_query(query, graphdb_url, repository_name)

def clean_repository_geojson_states(graphdb_url, repository_name, geojson_source, factoids_named_graph_name, permanent_named_graph_name, lang, geom_kg_file):
    factoids_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, factoids_named_graph_name)
    permanent_named_graph_uri = gd.get_named_graph_uri_from_name(graphdb_url, repository_name, permanent_named_graph_name)

    # Détection des arrondissements et quartiers qui ont un hiddenLabel similaire
    # Faire de même avec les codes postaux et les voies
    landmark_types = [np.LTYPE["District"], np.LTYPE["PostalCodeArea"], np.LTYPE["Thoroughfare"]]
    for ltype in landmark_types:
        msp.merge_similar_landmarks_with_hidden_labels(graphdb_url, repository_name, ltype, factoids_named_graph_uri)

    msp.merge_similar_landmark_relations(graphdb_url, repository_name, factoids_named_graph_uri)
    msp.detect_similar_time_interval_of_landmarks(graphdb_url, repository_name, np.SKOS["exactMatch"], factoids_named_graph_uri)

    # Fusion des géométries (union) pour les landmarks qui ont plusieurs géométries
    msp.merge_landmark_multiple_geometries(graphdb_url, repository_name, factoids_named_graph_uri, geom_kg_file)

    # # L'URI ci-dessous définit la source liée au fichier
    geojson_source_uri = URIRef(gr.generate_uri(np.FACTS, "SRC"))
    create_source_geojson_states(graphdb_url, repository_name, geojson_source_uri, permanent_named_graph_uri, geojson_source, np.FACTS)

    # Transfert de triplets non modifiables vers le graphe nommé permanent
    msp.transfert_immutable_triples(graphdb_url, repository_name, factoids_named_graph_uri, permanent_named_graph_uri)

    # # Ajout de liens entre les ressources de type repère et la source
    geojson_source_prov_uri = URIRef(gr.generate_uri(np.FACTS, "PROV"))
    create_source_provenances_geojson(graphdb_url, repository_name, geojson_source_uri, geojson_source_prov_uri, factoids_named_graph_uri, permanent_named_graph_uri)
