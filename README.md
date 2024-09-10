# PErpetual GAZeteer of approach-address UtteranceS

This repository contains the documentation of the PeGaZus ontology and knowledge graph construction method.

## Structure of the repository
```
├── data                      <- RDF resources used to build the graph
<<<<<<< HEAD
│   ├── addresses                 <- RDF resources for the specific case of addresses and streets
│   ├── cadaster                  <- RDF resources for the specific case of the plots from the Napoleonic land registry
│
├── ontology                  <- PeGaZus Ontology
│   ├── ontology-addresses.ttl    <- Core part of the ontology to describe landmarks and addresses
│   ├── ontology-cadastre.ttl     <- Specific modules used to describe the Napoleonic land registry documents and landmarks
=======
│   ├── addresses                   <- RDF resources for the specific case of addresses and streets
│   ├── land-registry               <- RDF resources for the specific case of the plots from the Napoleonic land registry
│
├── ontology                  <- PeGaZus Ontology
│   ├── ontology-address.ttl         <- Core part of the ontology to describe landmarks and addresses
│   ├── ontology-land-registry.ttl   <- Specific modules used to describe the Napoleonic land registry documents and landmarks
>>>>>>> b6ea87bf2816fb84e2bcaf5122a978db59b7a44f
│   ├── documentation
│       ├── addresses
│           ├── land_registry_landmarks_extension
│       ├── land_registry_documents_use
│       ├── sources
│       ├── taxpayers
│       ├── temporal_evolution
│
├── scripts
<<<<<<< HEAD
│   ├── cadaster                  <- Implementation of the algorithm specialized for the Napoleonic land registry dataset
│   ├── addresses                 <- Implementation of the algorithm specialized for addresses and streets
=======
│   ├── addresses                    <- Implementation of the algorithm specialized for the addresses
│   ├── land-registry                <- Implementation of the algorithm specialized for the Napoleonic land registry
>>>>>>> b6ea87bf2816fb84e2bcaf5122a978db59b7a44f
│
└── README.md
```

## Acknowledgements
This work was supported by the IGN and the AID.
