# 5. Clean knowledge graph
## 7.1 [NOT FOR THE MOMENT] Add root landmark has a trace of aggregation landmark
```
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>

INSERT { GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
    ?aggLandmark add:hasTrace ?root.
    ?root add:isTraceOf ?aggLandmark.
    }}
WHERE {
    SELECT distinct ?aggLandmark ?root WHERE {
        GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations>{
        ?aggLandmark a add:Landmark; add:isLandmarkType cad_ltype:Plot .  }
        ?otherLandmark add:hasRootLandmark ?root . 
    }
    GROUP BY ?aggLandmark ?root}
```

## 7.2 Delete tmp named graphs related to attributes versions
* We can delete all the *http://rdf.geohistoricaldata.org/tmp/XXXXX* named graphs :
    * *http://rdf.geohistoricaldata.org/tmp/natureattributeversions*
    * *http://rdf.geohistoricaldata.org/tmp/addressattributeversions*
    * *http://rdf.geohistoricaldata.org/tmp/taxpayerattributeversions*
    * *etc.*

## 7.3 Clean tmp properties related to landmarks
* To be shure
```sparql
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
DELETE {
    ?obj add:hasAggregateLabel ?obj2
    }
WHERE {
    ?obj add:hasAggregateLabel ?obj2
}
```
* Execute the following request : 
```sparql
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
DELETE {
    ?obj add:hasMergedValue ?obj2
    }
WHERE {
    ?obj add:hasMergedValue ?obj2
}
```