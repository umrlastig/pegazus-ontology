# README.md

## Historical sources
Use cases presented to asses the PeGaZus ontology and KG construction method are the followings.

### Plots use case
**Sources**
* Napoleonic land registry of Gentilly (1810-1848) inclusing cadastral index maps and mutation registers (Departemental Archives of Val-de-Marne)
* Napoleonic land registry of Gentilly (1845-1860) inclusing cadastral index maps and mutation registers (Departemental Archives of Val-de-Marne and Paris Archives)

**RDF Resources creation**
* Geometries : Plots have been digitized by hand using georeferenced cadastral index maps of previous project. This includes :
    * Vectorization of the plots
    * Association of each plot with a plot number
* Other informations have been transcribed by hand in several mutation registers
* Sources (maps and registers) object have been created using archives metadata

## Initial named graphs used to build the final KG

* **Ontology**
```sparql
http://rdf.geohistoricaldata.org/ontology
```

    - ontology-adresse.ttl
    - ontology-cadastre.ttl
    - activities.ttl

* Plots (**root plots** created from maps and/or initial registers)
```sparql
http://rdf.geohistoricaldata.org/rootlandmarks
``` 
    - Gentilly_landmarks_initial_plots.ttl

* Plots (**plots versions** created from mutation registers)
```sparql
http://rdf.geohistoricaldata.org/landmarksversions
``` 
    - Gentilly_landmarks_plot_mentions.ttl
    - Gentilly_sources_folios.ttl
    - Gentilly_sources_pages.ttl
    - Gentilly_owners_cf_clas_mut.ttl

* **Other landmarks** (towns, cadastral sections, streets etc.)
```sparql
http://rdf.geohistoricaldata.org/otherlandmarks
``` 
    - landmarks.ttl
    - Gentilly_landmarks_lieu_dit.ttl

* **Sources (root sources)**
```sparql
http://rdf.geohistoricaldata.org/sources
``` 
    - sources.ttl