# README.md

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
http://rdf.geohistoricaldata.org/relatedlandmarks
``` 
    - Gentilly_landmarks_plot_mentions.ttl
    - Gentilly_sources_folios.ttl
    - Gentilly_sources_pages.ttl
    - Gentilly_owners_cf_clas_mut.ttl

* **Other landmarks** (towns, cadastral sections, streets, etc.)
```sparql
http://rdf.geohistoricaldata.org/otherslandmarks
``` 
    - landmarks.ttl
    - Gentilly_landmarks_lieu_dit.ttl

* **Sources (registres et images)**
```sparql
http://rdf.geohistoricaldata.org/sources
``` 
    - sources.ttl