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

## 3. Which plots are mentioned in a given folio?
```sparql
PREFIX source: <http://rdf.geohistoricaldata.org/id/source/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>

SELECT DISTINCT ?plot ?id ?folio ?numFolio ?matrice ?matriceName
WHERE {
    ?folio a rico:RecordResource.
    ?folio cad:isSourceType/skos:broader srctype:Folio.
    ?folio cad:hasNumFolio ?numFolio.
    #Register details
    ?folio rico:isOrWasConstituentOf+/rico:isOrWasIncludedIn ?matrice.
    ?matrice cad:isSourceType ?matriceType.
    ?matrice rico:name ?matriceLabel.
    ?matrice rico:location ?matriceArea.
    BIND(CONCAT(?matriceLabel, ', ', ?matriceArea) AS ?matriceName)
    FILTER(?numFolio = '236' && ?matrice = source:94_Gentilly_MAT_B_NB_1813)
    #Plot
    ?folio rico:hasOrHadConstituent+ ?classement.
    ?classement cad:mentions/add:isAttributeVersionOf/add:isAttributeOf/add:isTraceOf ?plot.
    ?plot dcterms:identifier ?id.
} 
```
## 4. Which taxpayers are mentioned in a given folio?
```sparql 
PREFIX source: <http://rdf.geohistoricaldata.org/id/source/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>

SELECT DISTINCT ?taxpayer ?label ?folio ?numFolio ?matrice ?matriceName
WHERE {
    ?folio a rico:RecordResource.
    ?folio cad:isSourceType/skos:broader srctype:Folio.
    ?folio cad:hasNumFolio ?numFolio.
    #Register details
    ?folio rico:isOrWasConstituentOf+/rico:isOrWasIncludedIn ?matrice.
    ?matrice cad:isSourceType ?matriceType.
    ?matrice rico:name ?matriceLabel.
    ?matrice rico:location ?matriceArea.
    BIND(CONCAT(?matriceLabel, ', ', ?matriceArea) AS ?matriceName)
    FILTER(?numFolio = '236' && ?matrice = source:94_Gentilly_MAT_B_NB_1813)
    #Taxpayers
    ?folio rico:hasOrHadConstituent+ ?mutation.
    ?mutation add:hasAttribute/add:hasAttributeVersion/cad:hasTaxpayer/add:isTraceOf ?taxpayer.
    ?taxpayer rdfs:label ?label.
} 
```

## 5. Which table lines are crossed out ?
```sparql
PREFIX mlclasse: <http://rdf.geohistoricaldata.org/id/codes/cadastre/mlClasse/>
PREFIX cad_spval: <http://rdf.geohistoricaldata.org/id/codes/cadastre/specialCellValue/>
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
select * where {
    ?classement a rico:RecordResource.
    ?classement cad:isSourceType srctype:ArticleDeClassement.
    ?classement rico:hasOrHadInstantiation ?i.
    ?i cad:hasClasse/cad:hasClasseValue mlclasse:CrossedOut.
} 
```

## 6. Which plot versions is taken from a left-over of an other plot version ?
```
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX cad_spval: <http://rdf.geohistoricaldata.org/id/codes/cadastre/specialCellValue/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>

select * 
where {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksversions> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
    }
    ?plot add:hasAttribute/add:hasAttributeVersion/cad:takenFrom cad_spval:ResteSV.
} 
```