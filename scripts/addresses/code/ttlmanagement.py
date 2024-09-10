from rdflib import Graph, URIRef
import re

def elem_is_valid(elem):
    if isinstance(elem, URIRef):
        return uri_is_valid(elem)
    return True

def uri_is_valid(uri:URIRef):
    str_uri = str(uri)
    pattern = ".{0,}#.{0,}#.{0,}"
    matches = re.match(pattern, str_uri)
    if matches is None:
        return True
    else:
        return False

def format_ttl_to_avoid_invalid_iri_value_error(in_ttl_file:str, out_ttl_file:str=None):
    """
    Reformattage d'un fichier ttl en supprimant les triplets problématiques lors de l'import du fichier.
    Éviter l'erreur `org.eclipse.rdf4j.sail.SailException: Invalid IRI value` due à des IRI avec deux `#`.
    Si `out_ttl_file` n'est pas renseigné, `in_ttl_file` est écrasé.
    """

    g = Graph()
    g.parse(in_ttl_file)

    # Pour chaque triplet, on regarde si les URI y sont valides.
    # On supprime le triple si une d'entre elles ne l'est pas
    for s, p, o in g:
        remove_triple = False
        remove_triple = not elem_is_valid(s)
        remove_triple = not elem_is_valid(p)
        remove_triple = not elem_is_valid(o)
        if remove_triple:
            g.remove((s,p,o))

    if out_ttl_file is None:
        out_ttl_file = in_ttl_file

    g.serialize(out_ttl_file)