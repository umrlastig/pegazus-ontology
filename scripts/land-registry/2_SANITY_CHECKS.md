# Data sanity checks

## Before updating initial data
### 1. Assert End date is not before start date
> Should return 0 results.
```sparql
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>

SELECT * WHERE { 
	?plot a addr:Landmark; addr:isLandmarkType cad_ltype:Plot .
    ?plot addr:hasTime/addr:hasBeginning/addr:timeStamp ?start.
    ?plot addr:hasTime/addr:hasEnd/addr:timeStamp ?end.
    FILTER(?start > ?end)
} 
```
## During updating initial data
```sparql
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>

select * where {
    ?cf a rico:RecordPart; cad:isSourceType srctype:CompteFoncier.
    ?cf addr:hasTime/addr:hasBeginning/addr:timeStamp ?start.
    ?cf addr:hasTime/addr:hasEnd/addr:timeStamp ?end.
    ?cf rico:hasOrHadConstituent ?mutation.
    ?mutation addr:hasAttribute ?a.
    ?a addr:hasAttributeVersion ?v.
    ?v cad:hasTaxpayer ?taxpayer.
    ?v addr:isMadeEffectiveBy/addr:dependsOn ?event1.
    ?v addr:isOutdatedBy/addr:dependsOn ?event2.
    #?event1 addr:hasTime/addr:timeStamp ?t1.
    #?event2 addr:hasTime/addr:timeStamp ?t2.
}
ORDER By ?taxpayer ?mutation
```