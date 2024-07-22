# SPARQL queries for the *Addresses* modelet

SPARQL queries describing informal competence questions

## To find out all the addresses located along a street defined by a label

What are the addresses located along the Gérard Street (rue Gérard)?
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX ltype: <http://rdf.geohistoricaldata.org/id/codes/address/landmarkType/>
PREFIX atype: <http://rdf.geohistoricaldata.org/id/codes/address/attributeType/>

SELECT DISTINCT ?address ?addressLabel ?geom WHERE {
    BIND("rue Gérard" AS ?streetLabel)
    BIND("fr" AS ?streetLang)
    ?lm a addr:Landmark ; addr:isLandmarkType ltype:Thoroughfare; rdfs:label ?streetName.
    FILTER(LCASE(STR(?streetName)) = LCASE(?streetLabel) && LANG(?streetName) = ?streetLang)
    ?address a addr:Address; addr:hasStep [a addr:AddressSegment; addr:relatum ?lm] ; rdfs:label ?addressLabel.
    OPTIONAL {?address addr:targets [addr:hasAttribute [addr:isAttributeType atype:Geometry ; addr:hasAttributeVersion [addr:versionValue ?geom]]].}
}
```

## To find out the coordinates for an address according to its wording

What are the coordinates of the target of an address written as ‘41 rue de Rivoli, 75001 Paris 1er arrondissement’?
```sparql
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX atype: <http://rdf.geohistoricaldata.org/id/codes/address/attributeType/>

SELECT ?item ?addressLabel ?geom WHERE {
    BIND("50 rue Gérard, 75013 Paris 13e Arrondissement" AS ?addrLabel)
    BIND("fr" AS ?addrLang)
    ?item a addr:Address;
    rdfs:label ?addressLabel;
    addr:targets [addr:hasAttribute [addr:isAttributeType atype:Geometry ; addr:hasAttributeVersion [addr:versionValue ?geom]]].
    FILTER(LCASE(STR(?addressLabel)) = LCASE(?addrLabel) && LANG(?addressLabel) = ?addrLang)
}
```

## For a list of addresses within a given geographical area

What are the addresses located within the area defined by the following WKT `POLYGON ((2.353134 48.830133, 2.353354 48.829717, 2.35249 48.829378, 2.352056 48.82953, 2.352619 48.829897, 2.353134 48.830133))` expressed in the WGS84 coordinate system.

```sparql
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX atype: <http://rdf.geohistoricaldata.org/id/codes/address/attributeType/>

SELECT DISTINCT ?addr ?addrLabel ?geom WHERE {
    BIND("<http://www.opengis.net/def/crs/OGC/1.3/CRS84> POLYGON ((2.353134 48.830133, 2.353354 48.829717, 2.35249 48.829378, 2.352056 48.82953, 2.352619 48.829897, 2.353134 48.830133))"^^geo:wktLiteral AS ?area)
    ?addr a addr:Address ; rdfs:label ?addrLabel ; addr:targets [addr:hasAttribute [addr:isAttributeType atype:Geometry ; addr:hasAttributeVersion [addr:versionValue ?geom]]] .
    FILTER (geof:sfWithin(?geom, ?area))
}
```
