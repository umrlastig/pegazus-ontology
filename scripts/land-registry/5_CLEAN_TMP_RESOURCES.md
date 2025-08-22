# 5. Clean knowledge graph
## 7.1 [NOT FOR THE MOMENT] Add root landmark has a trace of aggregation landmark
```
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>

INSERT { GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations> {
    ?aggLandmark addr:hasTrace ?root.
    ?root addr:isTraceOf ?aggLandmark.
    }}
WHERE {
    SELECT distinct ?aggLandmark ?root WHERE {
        GRAPH <http://rdf.geohistoricaldata.org/landmarksaggregations>{
        ?aggLandmark a addr:Landmark; addr:isLandmarkType cad_ltype:Plot .  }
        ?otherLandmark addr:hasRootLandmark ?root . 
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
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
DELETE {
    ?obj addr:hasAggregateLabel ?obj2
    }
WHERE {
    ?obj addr:hasAggregateLabel ?obj2
}
```
* Execute the following request : 
```sparql
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
DELETE {
    ?obj addr:hasMergedValue ?obj2
    }
WHERE {
    ?obj addr:hasMergedValue ?obj2
}
```