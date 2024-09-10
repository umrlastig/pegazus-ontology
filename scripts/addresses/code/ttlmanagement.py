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
    Reformatting a ttl file by deleting problematic triplets when importing the file.
    Avoid error `org.eclipse.rdf4j.sail.SailException: Invalid IRI value` due to IRIs with two `#`.
    If `out_ttl_file` is not set, `in_ttl_file` is overwritten.
    """

    g = Graph()
    g.parse(in_ttl_file)

    # For each triple, we check whether the URIs are valid.
    # We delete the triple if one of them is not valid.
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