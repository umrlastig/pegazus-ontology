# PErpetual GAZeteer of approach-address UtteranceS

This repository contains the documentation of the PeGaZus ontology and knowledge graph construction method. 

## Structure of the repository
```
├── data                      <- RDF resources used to build the graph
│   ├── addresses                   <- RDF resources for the specific case of addresses and streets
│   ├── land-registry               <- RDF resources for the specific case of the plots from the Napoleonic land registry
│
├── ontology                  <- PeGaZus Ontology
│   ├── ontology-addresses.ttl       <- Core part of the ontology to describe landmarks and addresses
│   ├── ontology-land-registry.ttl   <- Specific modules used to describe the Napoleonic land registry documents and landmarks
│   ├── documentation
│
├── scripts                   <- Script to construct the knowledge graph
│   ├── addresses                    <- Implementation of the algorithm specialized for addresses and streets
│   ├── land-registry                <- Implementation of the algorithm specialized for the Napoleonic land registry
│
└── README.md
```

## Acknowledgements
This work was supported by the IGN and the AID.
