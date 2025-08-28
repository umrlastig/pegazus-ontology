## Taxpayers SPARQL Requests
* The following requests are used to answer to the competency questions.

### 1. Who are the taxpayers of the municipality X?
* Example : Taxpayers in Gentilly
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX cad_atype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/attributeType/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>

#List of the taxpayers of a given commune
SELECT DISTINCT ?taxpayer (SAMPLE(?taxpayerLabel) AS ?label) 
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
    ?plot a addr:Landmark; addr:isLandmarkType cad_ltype:Plot.}
    #Select the commune
    ?lr addr:locatum ?plot; addr:relatum ?section.
    ?lr2 addr:locatum ?section; addr:relatum ?commune.
    ?commune rdfs:label ?communeName
    FILTER(?communeName = 'Gentilly')
    #Get the taxpayers
    ?plot addr:hasAttribute[addr:hasAttributeVersion/cad:hasTaxpayer ?taxpayer].
    ?taxpayer rdfs:label ?taxpayerLabel.
}
GROUP BY ?taxpayer
ORDER BY ?label
```
* 184 taxpayers are responsible of at least one plot in the area of study.

### 2. Who are the taxpayers of plot X in section XX of a given municipality?
* Example : plot D-19 in Gentilly, section D (cadastre of 1845)
* NB : this include the taxpayers of the initial plot and of all the possible splits of this plot
```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX cad_atype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/attributeType/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>

SELECT DISTINCT ?taxpayer (SAMPLE(?taxpayerLabel) AS ?label) 
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
    ?plot a addr:Landmark; addr:isLandmarkType cad_ltype:Plot.}
    ?plot dcterms:identifier ?id.
    FILTER(regex(?id, 'D-19p') || regex(?id, 'D-19$')) 
    #Select the commune
    ?lr addr:locatum ?plot; addr:relatum ?section.
    ?lr2 addr:locatum ?section; addr:relatum ?commune.
    ?commune rdfs:label ?communeName
    FILTER(?communeName = 'Gentilly')
    #Get the taxpayers
    ?plot addr:hasAttribute[addr:hasAttributeVersion/cad:hasTaxpayer ?taxpayer].
    ?taxpayer rdfs:label ?taxpayerLabel.
}
GROUP BY ?taxpayer
ORDER BY ?Label
```
* 6 taxpayers are associated with D-19 (Gentilly) plot.s.

### 3. Who are the taxpayers living in a given commune?
* Example : taxpayers in Gentilly living in Paris
* NB : taxpayers address is not mentionned in all the documents, its an uncomplete overview of taxpayers's addresses
```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX cad_atype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/attributeType/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>

SELECT DISTINCT ?taxpayer (SAMPLE(?taxpayerLabel) AS ?label) (SAMPLE(?taxpayerAddress) AS ?address)
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
    ?plot a addr:Landmark; addr:isLandmarkType cad_ltype:Plot.}
    #Select the commune where the plot is located
    ?lr addr:locatum ?plot; addr:relatum ?section.
    ?lr2 addr:locatum ?section; addr:relatum ?commune.
    ?commune rdfs:label ?communeName
    FILTER(?communeName = 'Gentilly')
    #Get the taxpayers
    ?plot addr:hasAttribute[addr:hasAttributeVersion/cad:hasTaxpayer ?taxpayer].
    ?taxpayer rdfs:label ?taxpayerLabel.
    ?taxpayer cad:taxpayerAddress ?taxpayerAddress
    FILTER(regex(lcase(?taxpayerAddress),'paris'))
}
GROUP BY ?taxpayer
ORDER BY ?Label
```
* 35 taxpayers (among the ones the address is given) are living in Paris.

### 4. Who are the taxpayers of a given commune whose profession is XX ?
* Taxpayers in Gentilly who have an activity related to the wine.
```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX cad_atype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/attributeType/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>

SELECT DISTINCT ?taxpayer (SAMPLE(?taxpayerLabel) AS ?label) (SAMPLE(?taxpayerActivity) AS ?activity)
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
    ?plot a addr:Landmark; addr:isLandmarkType cad_ltype:Plot.}
    #Select the commune where the plot is located
    ?lr addr:locatum ?plot; addr:relatum ?section.
    ?lr2 addr:locatum ?section; addr:relatum ?commune.
    ?commune rdfs:label ?communeName
    FILTER(?communeName = 'Gentilly')
    #Get the taxpayers
    ?plot addr:hasAttribute[addr:hasAttributeVersion/cad:hasTaxpayer ?taxpayer].
    ?taxpayer rdfs:label ?taxpayerLabel.
    ?taxpayer cad:taxpayerActivity ?taxpayerActivity
    FILTER(regex(lcase(?taxpayerActivity),'vin'))
}
GROUP BY ?taxpayer
```
* 8 taxpayers have an activity related to wine (amng the ones the activity is given in the documents)