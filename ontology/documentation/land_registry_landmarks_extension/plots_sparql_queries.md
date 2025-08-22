# SPARQL requests of the Land Registry Landmarks extension

## 1. Which are the plots located in a given area (commune/section) ?
* List of plots in Gentilly
```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT distinct ?plot (SAMPLE(?id) AS ?ID)
WHERE {
    {GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
	}} UNION {
	GRAPH <http://rdf.geohistoricaldata.org/rootlandmarks> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
    }
	}
    ?plot dcterms:identifier ?id.
    #Select the commune where the plot is located
    ?lr add:locatum ?plot; add:relatum ?section.
    ?lr2 add:locatum ?section; add:relatum ?commune.
    ?commune rdfs:label ?communeName
    FILTER(?communeName = 'Gentilly')
}
GROUP BY ?plot
ORDER BY ?ID
```

## 2. How many plots are there in a given commune ?
* There are two possible interpretation of this request :
    * Number of plots on the map (at the creation of the cadastre)
    * Number of plots over the cadastre validity period

### 2.1 Number of plots according to the maps

```sparql
SELECT  (count(distinct ?plot) AS ?count)
WHERE {
	GRAPH <http://rdf.geohistoricaldata.org/rootlandmarks> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
	}
    #Select the commune where the plot is located
    ?lr add:locatum ?plot; add:relatum ?section.
    ?lr2 add:locatum ?section; add:relatum ?commune.
    ?commune rdfs:label ?communeName
    FILTER(?communeName = 'Gentilly')
}
```
* Note it is possible to combine the two numbers

### 2.2 Number of plots according to the registers
```sparql
SELECT  (count(distinct ?plot) AS ?count)
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
	}
    #Select the commune where the plot is located
    ?lr add:locatum ?plot; add:relatum ?section.
    ?lr2 add:locatum ?section; add:relatum ?commune.
    ?commune rdfs:label ?communeName
    FILTER(?communeName = 'Gentilly')
}
```

## 3. What is/are the nature.s of a plot XXX ?
* NB : plots ID never are updated in case of split or merge. It means that the request will return natures of 1..n parts of the plot which is drawn on the map.
```sparql
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX ctype: <http://rdf.geohistoricaldata.org/id/codes/address/changeType/>
SELECT ?plot ?id ?nature ?start ?end
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
		?plot dcterms:identifier ?id
	}
    #Select the commune where the plot is located
    ?lr add:locatum ?plot; add:relatum ?section.
    ?lr2 add:locatum ?section; add:relatum ?commune.
    ?commune rdfs:label ?communeName.
    
	#Nature attribute
    ?plot add:hasAttribute/add:hasAttributeVersion ?v.
    ?v cad:hasPlotNature ?nature.
    ?v add:isMadeEffectiveBy [add:isChangeType ctype:AttributeVersionAppearance;
    				  add:dependsOn ?event1].
	?v add:isOutdatedBy [add:isChangeType ctype:AttributeVersionDisappearance;
    				  add:dependsOn ?event2].
    ?event1 add:hasTime/add:timeStamp ?start.
    ?event2 add:hasTime/add:timeStamp ?end.

    #Filters
    FILTER(?communeName = 'Gentilly')
    FILTER(regex(?id, 'D-37$')||regex(?id,'D-37p')) 
}
ORDER BY ?start ?end
```
## 4. What is/are the taxpayer.s of a plot XXX ?
* NB : plots ID never are updated in case of split or merge. It means that the request will return natures of 1..n parts of the plot drawn on the map.
```sparql
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX ctype: <http://rdf.geohistoricaldata.org/id/codes/address/changeType/>
SELECT ?plot ?id ?label ?v ?start ?end
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
		?plot dcterms:identifier ?id
	}
    #Select the commune where the plot is located
    ?lr add:locatum ?plot; add:relatum ?section.
    ?lr2 add:locatum ?section; add:relatum ?commune.
    ?commune rdfs:label ?communeName.
    
	#Taxpayer attribute
    ?plot add:hasAttribute/add:hasAttributeVersion ?v.
    ?v cad:hasTaxpayer ?taxpayer.
    ?taxpayer rdfs:label ?label.
    ?v add:isMadeEffectiveBy [add:isChangeType ctype:AttributeVersionAppearance;
    				  add:dependsOn ?event1].
	?v add:isOutdatedBy [add:isChangeType ctype:AttributeVersionDisappearance;
    				  add:dependsOn ?event2].
    ?event1 add:hasTime/add:timeStamp ?start.
    ?event2 add:hasTime/add:timeStamp ?end.

    #Filters
    FILTER(?communeName = 'Gentilly')
    FILTER(regex(?id, 'D-86$')||regex(?id,'D-86p')) 
}
ORDER BY ?start ?end
```

## 5. What is/are the address.es of a plot XXX ?
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX ctype: <http://rdf.geohistoricaldata.org/id/codes/address/changeType/>

SELECT ?plot ?id ?label ?v ?start ?end
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
		?plot dcterms:identifier ?id
	}
    #Select the commune where the plot is located
    ?lr add:locatum ?plot; add:relatum ?section.
    ?lr2 add:locatum ?section; add:relatum ?commune.
    ?commune rdfs:label ?communeName.
    
	#Taxpayer attribute
    ?plot add:hasAttribute/add:hasAttributeVersion ?v.
    ?v cad:hasPlotAddress/add:relatum ?address.
    ?address skos:prefLabel ?label.
    ?v add:isMadeEffectiveBy [add:isChangeType ctype:AttributeVersionAppearance;
    				  add:dependsOn ?event1].
	?v add:isOutdatedBy [add:isChangeType ctype:AttributeVersionDisappearance;
    				  add:dependsOn ?event2].
    ?event1 add:hasTime/add:timeStamp ?start.
    ?event2 add:hasTime/add:timeStamp ?end.

    #Filters
    FILTER(?communeName = 'Gentilly')
    FILTER(regex(?id, 'D-40$')||regex(?id,'D-40p')) 
}
ORDER BY ?start ?end
```
## 6. Which are the plots of nature XXX in a commune/section ?
```sparql
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX pnature: <http://rdf.geohistoricaldata.org/id/codes/cadastre/plotNature/>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX ctype: <http://rdf.geohistoricaldata.org/id/codes/address/changeType/>

SELECT ?plot ?id ?t1 ?t2
WHERE {
    GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
        ?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot.
		?plot dcterms:identifier ?id
	}
    #Select the commune where the plot is located
    ?lr add:locatum ?plot; add:relatum ?section.
    ?lr2 add:locatum ?section; add:relatum ?commune.
    ?commune rdfs:label ?communeName.
    
    ?plot add:hasAttribute/add:hasAttributeVersion ?v.
    ?v cad:hasPlotNature pnature:Jardin.
    ?v add:isMadeEffectiveBy [add:isChangeType ctype:AttributeVersionAppearance;
    				  add:dependsOn ?event1].
	?v add:isOutdatedBy [add:isChangeType ctype:AttributeVersionDisappearance;
    				  add:dependsOn ?event2].
    ?event1 add:hasTime/add:timeStamp ?t1.
    ?event2 add:hasTime/add:timeStamp ?t2.

    #Filters
    FILTER(?communeName = 'Gentilly')
	BIND(("1848-06-06"^^xsd:date) AS ?date)
	FILTER(?t1 <= ?date && ?t2 >= ?date)
}
ORDER BY ?id ?t1 ?t2
```