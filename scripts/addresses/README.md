# Multi-source ontology population
Populating the ontology using different sources

## Sources
The sources used here are :
* the City of Paris's street nomenclature;
* OpenStreetMap (OSM);
* Wikidata ;
* Base Adresse Nationale (BAN).
* various atlases of the city of Paris :
  * Napoleonic cadastre of Gentilly (1847)
  * Andriveau plan (1849)
  * municipal parcel map of Paris (1871)
  * municipal map of Paris (1888)

## `data` folder
This folder contains files which are used as starting data for the settlement. 12 files are required, the names of which are given in the notebook by the following variables:
* `vpta_csv_file_name`: file containing the names of the rights-of-way of the current Parisian thoroughfares;
* `vptc_csv_file_name`: file of names of obsolete City of Paris thoroughfares;
* `osm_csv_file_name`: file of data extracted from OpenStreetMap;
* `osm_hn_csv_file_name`: file of house number data from OpenStreetMap;
* `bpa_csv_file_name`: file from BAN;
* `wdp_land_csv_file_name`: file of geographical entities from Wikidata (thoroughfares, districts, cities) ;
* `wdp_loc_csv_file_name`: file of geographical entity relations (between thoroughfares and areas) from Wikidata ;
* `cn_1847_geojson_file_name`: file of data from Napoleonic cadastre of 1847 ;
* `an_1849_geojson_file_name`: file of data from Andriveau map ;
* `pm_1871_geojson_file_name`: file of data from 1871 municipal parcel map ;
* `am_1888_geojson_file_name`: file of data from the 1888 Municipal Atlas plan.

How to obtain some of theses files is shown below.

### Base Adresse Nationale

Data from [Base Adresse Nationale (BAN)](https://adresse.data.gouv.fr/base-adresse-nationale) are available [here](https://adresse.data.gouv.fr/data/ban/adresses/latest/csv). For this project, downloaded data are related to Paris (`adresses-75.csv.gz`). File name must correspond to `bpa_csv_file_name` in the notebook.

### OpenStreetMap

Files are the results of two queries from [OSM planet SPARQL endpoint](https://qlever.cs.uni-freiburg.de/osm-planet). See *Bast, H., Brosi, P., Kalmbach, J., & Lehmann, A. (2021, November). An efficient RDF converter and SPARQL endpoint for the complete OpenStreetMap data. In Proceedings of the 29th International Conference on Advances in Geographic Information Systems (pp. 536-539)*.

Extracted data from OpenStreetMap are :
* house numbers (_house numbers_) : their value (a number and optionally a complement), their geometry, the thoroughfare or the district they belong to ;
* thoroughfares : their name
* districts : their name and INSEE code.

1. Extract Paris addresses
In the query interface, there are two queries to launch.
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

2. Export the result in two `csv` files and insert them in the folder defined by the `tmp_folder` variable. The file names must correspond to those defined in the notebook:
* for query 1, the name is linked to the `osm_csv_file_name` variable;
* for query 2, the name is linked to the `osm_hn_csv_file_name` variable.

### Wikidata
Via Wikidata, the extracted data are:
* geographical entities:
    * Paris thoroughfares (current and old ones) ;
    * areas linked to Paris:
      * districts of Paris ;
      * arrondissements (those before and after 1860) of Paris;
      * communes (past and present) of the former department of Seine;
* the relationships between these geographical entities.

Three files in CSV format must be stored in the `data` folder, the names of which are linked to variables in the notebook:
* `wdp_land_csv_file_name`: for of geographical entities (thoroughfares, districts, cities) ;
* `wdp_loc_csv_file_name`: file of geographical entity relations (between thoroughfares and areas).

Obtaining these files is straightforward. Simply run the `get_data_from_wikidata()` function defined in the notebook.

### Ville de Paris
* The data for the city of Paris is made up of two datasets:
* [dénominations des emprises des voies actuelles](https://opendata.paris.fr/explore/dataset/denominations-emprises-voies-actuelles)
* [dénominations caduques des voies](https://opendata.paris.fr/explore/dataset/denominations-des-voies-caduques)

The information used here is the names of the thoroughfares (and their geographical extent for current lanes) with their period of validity (if known).

The two datasets must be downloaded in CSV format into the `data` folder and their names must correspond to the names given by the variables `vpta_csv_file_name` (for current lanes) and `vptc_csv_file_name` for obsolete lanes.

### Geojson files
You can get some of geojson files on [GeoHistoricalData](https://geohistoricaldata.org/) website. Click on `Download` then `Paris street networks` to download data. Then extract files you need.

## Launch the process
Once the files are in the `data` folder, the process can be started by running `multisource_population.ipynb` file.

⚠️ However, you need to ensure that GraphDB is installed and running during the process. [GraphDB](https://graphdb.ontotext.com/) is used to store and work on knowledge graphs. A variable is associated with the software: `graphdb_url` which is the URL of the web application.
