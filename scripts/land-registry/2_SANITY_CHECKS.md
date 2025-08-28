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
## 2. Check property account creation
* This request helps to visualise which taxpayers own the property accounts in each folio of each register.
* It should be executed after the notebook ```03-update-initial-data.ipynb```.
```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
PREFIX source: <http://rdf.geohistoricaldata.org/id/source/>

select * where {
    ?cf a rico:RecordPart; cad:isSourceType srctype:CompteFoncier.
    ?cf rico:isOrWasConstituentOf ?folio.
    ?folio cad:hasNumFolio ?folioid.
    ?cf dcterms:identifier ?id.
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
ORDER BY ?taxpayer ?mutation
```