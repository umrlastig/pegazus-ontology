# PErpetual GAZeteer of approach-address UtteranceS

This repository contains the documentation of the PeGaZus ontology and knowledge graph construction method. 

## Structure of the repository
```
├── data                      <- RDF resources used to build the graph
│   ├── addresses                   <- RDF resources for the specific case of addresses and streets
│   ├── land-registry               <- RDF resources for the specific case of the plots from the Napoleonic land registry
│
├── ontology                  <- PeGaZus Ontology
│   ├── ontology-addresses.ttl         <- Core part of the ontology to describe landmarks and addresses
│   ├── ontology-land-registry.ttl   <- Specific modules used to describe the Napoleonic land registry documents and landmarks
│   ├── documentation
│       ├── addresses
│           ├── land_registry_landmarks_extension
│       ├── land_registry_documents_use
│       ├── sources
│       ├── taxpayers
│       ├── temporal_evolution
│
├── scripts
│   ├── addresses                    <- Implementation of the algorithm specialized for the addresses
│   ├── land-registry                <- Implementation of the algorithm specialized for the Napoleonic land registry
│
└── README.md
```

## Historical sources
Use cases presented to asses the PeGaZus ontology and KG construction method are the followings.
### Addresses use case
TO BE ADD
### Plots use case
**Sources**
* Napoleonic land registry of Gentilly (1810-1848) inclusing cadastral index maps and mutation registers (Departemental Archives of Val-de-Marne)
* Napoleonic land registry of Gentilly (1845-1860) inclusing cadastral index maps and mutation registers (Departemental Archives of Val-de-Marne and Paris Archives)

**RDF Resources creation**
* Geometries : Plots have been digitized by hand using georeferenced cadastral index maps of previous project. This includes :
    * Vectorization of the plots
    * Association of each plot with a plot number
* Other informations have been transcribed by hand in several mutation registers
* Sources object have been created using archives metadata

## Acknowledgements
This work was supported by the IGN and the AID.
