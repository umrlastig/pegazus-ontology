# PErpetual GAZeteer of approach-address UtteranceS

This repository contains the documentation of the PeGaZus ontology and knowledge graph construction method. 

## Structure of the repository
```
├── data                      <- RDF resources used to build the graph
│   ├── addresses                   <- RDF resources for the specific case of addresses and streets
│   ├── cadaster                  <- RDF resources for the specific case of the plots from the Napoleonic land registry
│
├── ontology                  <- PeGaZus Ontology
│   ├── ontology-address.ttl      <- Core part of the ontology to describe landmarks and addresses
│   ├── ontology-cadastre.ttl     <- Specific modules used to describe the Napoleonic land registry documents and landmarks
│   ├── documentation
│
├── scripts
│   ├── addresses                  <- Implementation of the algorithm specialized for the addresses
│   ├── cadaster                  <- Implementation of the algorithm specialized for the Napoleonic land registry dataset
│
└── README.md
```

## Acknowledgements
This work was supported by the IGN and the AID.