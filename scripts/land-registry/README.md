# README

This folder contains 4 markdown files with the SPARQL requests specialized to build the KG of land plots.

## 1. Requirements
1. Create a ````cadastre``` repository in your Graph DB triplestore.
2. Add the [Ric-O ontology](https://github.com/ICA-EGAD/RiC-O/tree/master/ontology/current-version) into dedicated named graph (or default named graph)

## 2. Execution
### 2.1 Automated execution
Have a look to the ```code``` folder.

### 2.2 Manual executation using documentation
The algorithm files have to be executed in the following order :
1. Custom functions
2. Sanity checks
3. Update initial data
4. Build KG

Requests in *3_Update_Initial_data.md* and *4_Build_KG.md* can be executed automatically using the *python* scripts into the *python* folder.

#### 2.2.1 Initialisation
The following named graphs have to be created using the .rdf files in the *data/land-registry* folder of this repository.

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

## 3. Evaluation
SPARQL requests to answer the competency questions are in the *XXX_sparql_request.md* file of the */documentation/modelet_XXX* folder of this repository.
