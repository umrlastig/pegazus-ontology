from rdflib import Namespace

class NameSpaces():
    def __init__(self) -> None:
        self.__get_namespace_variables()
        self.__get_namespaces_with_prefixes()
        self.__get_query_prefixes_from_namespaces()

    def __get_namespace_variables(self):
        self.ADDR = Namespace("http://rdf.geohistoricaldata.org/def/address#")

        self.ATYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/address/attributeType/")
        self.LTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/address/landmarkType/")
        self.LRTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/address/landmarkRelationType/")
        self.CTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/address/changeType/")

        self.FACTS = Namespace("http://rdf.geohistoricaldata.org/id/address/facts/")
        self.FACTOIDS = Namespace("http://rdf.geohistoricaldata.org/id/address/factoids/")

        self.TIME = Namespace("http://www.w3.org/2006/time#")
        self.PROV = Namespace("http://www.w3.org/ns/prov#")
        self.RICO = Namespace("https://www.ica.org/standards/RiC/ontology#")
        self.GEO = Namespace("http://www.opengis.net/ont/geosparql#")
        self.GEOFLA = Namespace("http://data.ign.fr/def/geofla#")

        self.SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
        self.RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        self.XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
        self.OWL = Namespace("http://www.w3.org/2002/07/owl#")

    def __get_namespaces_with_prefixes(self):
        self.namespaces_with_prefixes = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Namespace):
                self.namespaces_with_prefixes[key.lower()] = value

    def __get_query_prefixes_from_namespaces(self):
        self.query_prefixes = ""
        for prefix, uri in self.namespaces_with_prefixes.items():
            str_uri = uri[""].n3()
            self.query_prefixes += f"PREFIX {prefix}: {str_uri}\n"
            