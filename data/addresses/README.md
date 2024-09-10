# README.md

## Initial data used to build the final KG

### BAN
File: `ban_adresses.csv`

Data from [Base Adresse Nationale (BAN)](https://adresse.data.gouv.fr/base-adresse-nationale) are available [here](https://adresse.data.gouv.fr/data/ban/adresses/latest/csv). For this project, downloaded data are related to Paris (`adresses-75.csv.gz`). Addresses selected from this file correspond to Buttes-aux-Cailles area. File name must correspond to `bpa_csv_file_name` in the notebook.

### OSM
Files: `osm_adresses.csv` and `osm_hn_adresses.csv`

These files are the results of two queries from [OSM planet SPARQL endpoint](https://qlever.cs.uni-freiburg.de/osm-planet). See *Bast, H., Brosi, P., Kalmbach, J., & Lehmann, A. (2021, November). An efficient RDF converter and SPARQL endpoint for the complete OpenStreetMap data. In Proceedings of the 29th International Conference on Advances in Geographic Information Systems (pp. 536-539)*.

Extracted data from OpenStreetMap are :
* house numbers (_house numbers_) : their value (a number and optionally a complement), their geometry, the thoroughfare or the district they belong to ;
* thoroughfares : their name
* districts : their name and INSEE code.

In the query interface, there are two queries to launch to extract Paris addresses.
* Query 1 :
```
PREFIX osmrel: <https://www.openstreetmap.org/relation/>
PREFIX osmkey: <https://www.openstreetmap.org/wiki/Key:>
PREFIX osmrdf: <https://osm2rdf.cs.uni-freiburg.de/rdf/member#>
PREFIX osm: <https://www.openstreetmap.org/>
PREFIX ogc: <http://www.opengis.net/rdf#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?houseNumberId ?streetId ?streetName ?arrdtId ?arrdtName ?arrdtInsee
 WHERE {
  ?selectedArea osmkey:wikidata "Q90"; ogc:sfContains ?houseNumberId.
  ?houseNumberId osmkey:addr:housenumber ?housenumberName.
  ?arrdtId ogc:sfContains ?houseNumberId; osmkey:name ?arrdtName; osmkey:ref:INSEE ?arrdtInsee; osmkey:boundary "administrative"; osmkey:admin_level "9"^^xsd:int .
  ?streetId osmkey:type "associatedStreet"; osmrel:member ?member; osmkey:name ?streetName.
  ?member osmrdf:role "house"; osmrdf:id ?houseNumberId.
}
```

* Query 2 :
```
PREFIX osmkey: <https://www.openstreetmap.org/wiki/Key:>
PREFIX ogc: <http://www.opengis.net/rdf#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>

SELECT DISTINCT ?houseNumberId ?houseNumberLabel ?houseNumberGeomWKT
 WHERE {
  ?selectedArea osmkey:wikidata "Q90"; ogc:sfContains ?houseNumberId.
  ?houseNumberId osmkey:addr:housenumber ?houseNumberLabel; geo:hasGeometry ?houseNumberGeom.
  ?houseNumberGeom geo:asWKT ?houseNumberGeomWKT.
}
```

The queries select all the house numbers in Paris, but it is possible to change the extraction zone by modifying the `osmkey:wikidata ‘Q90’` condition. For example, you can replace it with `osmkey:wikidata ‘Q2378493’` to restrict it to the Maison Blanche district of Paris (district where is Butte-aux-Cailles area is located). Note that only building numbers belonging to an `associatedStreet` type relationship and having the `house` role in this relationship are selected. For each query, results are exported to `csv` files: `osm_adresses.csv` for query 1 and `osm_hn_adresses.csv` for query 2. There are two queries instead of one because, endpoint is not able to return any result (due to limited performances).

### Wikidata
Files: `wd_paris_landmarks.csv` and `wd_paris_locations.csv`

Via Wikidata, the extracted data are:
* geographical entities:
    * Paris thoroughfares (current and old ones) ;
    * areas linked to Paris:
      * districts of Paris ;
      * arrondissements (those before and after 1860) of Paris;
      * communes (past and present) of the former department of Seine;
* the relationships between these geographical entities.

Obtaining these files is straightforward. Simply run the `get_data_from_wikidata()` function defined in the notebook. To avoid calling Wikidata SPARQL endpoint each time notebook is run and keeping all data of Paris, function can be commented.

### Ville de Paris
Files: `denominations-emprises-voies-actuelles.csv` and `denominations-des-voies-caduques.csv`

* the first file comes from [dénominations des emprises des voies actuelles](https://opendata.paris.fr/explore/dataset/denominations-emprises-voies-actuelles) which a list of current names of thoroughfares of Paris.
* the second one comes from [dénominations caduques des voies](https://opendata.paris.fr/explore/dataset/denominations-des-voies-caduques) which a list of former names of thoroughfares (current and old) of Paris.

For this work, we kept thoroughfares around Buttes-aux-Cailles district.

### Geojson files
Geojson files are geometrical data of an area (here Buttes-aux-Cailles) at a given time.

Files:
* `1847_cadastre_nap.geojson`: thoroughfares around 1847 according napoleonian cadaster ;
* `1849_andriveau.geojson`: thoroughfares around 1849 according Andriveau atlas ;
* `1871_plan_parcellaire_mun.geojson`: thoroughfares around 1871 according plan parcellaire municipal de Paris (municipal parcel map of Paris) ;
* `1888_atlas_municipal.geojson`: thoroughfares around 1888 according municipal atlas of Paris.
