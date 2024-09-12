# SPARQL requests of the land registry documents use modelet

## 1. Which folios mention plot X ?
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
SELECT DISTINCT ?folio ?numFolio ?matrice ?matriceName ?matriceType
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
        ?plot dcterms:identifier ?id
        FILTER(regex(?id,'D-19$') || regex(?id,'D-19p'))
    }
    #Folio details
    ?plot add:hasAttribute/add:hasAttributeVersion/cad:isMentionnedIn/rico:isOrWasConstituentOf+ ?folio.
    ?folio cad:isSourceType/skos:broader srctype:Folio.
    ?folio cad:hasNumFolio ?numFolio.
    #Register details
    ?folio rico:isOrWasConstituentOf+/rico:isOrWasIncludedIn ?matrice.
    ?matrice cad:isSourceType ?matriceType.
    ?matrice rico:name ?matriceLabel.
    ?matrice rico:location ?matriceArea.
    BIND(CONCAT(?matriceLabel, ', ', ?matriceArea) AS ?matriceName)
} 
```

## 2. Which folios mention taxpayer X ?
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
SELECT DISTINCT ?folio ?numFolio ?matrice ?matriceName ?matriceType
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/taxpayersaggregations> {
        ?taxpayer a cad:Taxpayer.
        ?taxpayer rdfs:label ?label
        FILTER(regex(lcase(?label),'^delon$'))
    }
    #Folio details
    ?taxpayer add:hasTrace ?taxpayerversion.
    ?taxpayerversion cad:fromSource/rico:isOrWasConstituentOf+ ?folio.
    ?folio cad:isSourceType/skos:broader srctype:Folio.
    ?folio cad:hasNumFolio ?numFolio.
    #Register details
    ?folio rico:isOrWasConstituentOf+/rico:isOrWasIncludedIn ?matrice.
    ?matrice cad:isSourceType ?matriceType.
    ?matrice rico:name ?matriceLabel.
    ?matrice rico:location ?matriceArea.
    BIND(CONCAT(?matriceLabel, ', ', ?matriceArea) AS ?matriceName)
} 
```