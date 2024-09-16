# Data sanity checks

## Before updating initial data
### 1. Assert End date is not before start date
> Should return 0 results.
```sparql
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>

SELECT * WHERE { 
	?plot a add:Landmark; add:isLandmarkType cad_ltype:Plot .
    ?plot add:hasTime/add:hasBeginning/add:timeStamp ?start.
    ?plot add:hasTime/add:hasEnd/add:timeStamp ?end.
    FILTER(?start > ?end)
} 
```
## During updating initial data
```sparql
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX add: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>

select * where {
    ?cf a rico:RecordPart; cad:isSourceType srctype:CompteFoncier.
    ?cf add:hasTime/add:hasBeginning/add:timeStamp ?start.
    ?cf add:hasTime/add:hasEnd/add:timeStamp ?end.
    ?cf rico:hasOrHadConstituent ?mutation.
    ?mutation add:hasAttribute ?a.
    ?a add:hasAttributeVersion ?v.
    ?v cad:hasTaxpayer ?taxpayer.
    ?v add:isMadeEffectiveBy/add:dependsOn ?event1.
    ?v add:isOutdatedBy/add:dependsOn ?event2.
    #?event1 add:hasTime/add:timeStamp ?t1.
    #?event2 add:hasTime/add:timeStamp ?t2.
}
ORDER By ?taxpayer ?mutation
```