# Data sanity checks

## 1. Assert End date is not before start date
Should return 0 results.
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
