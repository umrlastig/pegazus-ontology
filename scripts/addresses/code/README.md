# `code` folder
This folder is composed of multiple python files to create and manage knowledge graph:
* `attributeversioncomparisons.py`: functions to compare attribute version thanks to their values ;
* `curl.py`: functions to create curl commands to get access to GraphDB API ;
* `factoidscreations.py`: functions to create graphs from different data, they are used for a specific source ;
* `filemanagement.py`: read or write files (csv, json, ttl...) ;
* `geomprocessing.py`: functions to work with WKT geometries in knowledge graph ;
* `graphdb.py`: functions to make actions via GraphDB API (make queries, remove named graph...) ;
* `graphrdf.py`: construct knowledge graph thanks to RDFLib library
* `multisourceprocessing.py`: functions which centralize process of all other files to construct and manage knowledge graph ;
* `strprocessing.py`: functions to work with labels which are in the knowledge graph ;
* `timeprocessing.py`: functions about time : compare instants, intevals... ;
* `wikidata.py`: functions get access to SPARQL endpoint of Wikidata.