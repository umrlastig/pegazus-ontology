# PErpetual GAZeteer of approach-address UtteranceS

This repository contains the documentation of the PeGaZus ontology and knowledge graph construction method. 

## Structure of the repository
```
├── data                      <- RDF resources used to build the graph
│   ├── addresses                   <- raw resources for the specific case of addresses and streets
│   ├── land-registry               <- RDF resources for the specific case of the plots from the Napoleonic land registry
│
├── ontology                  <- PeGaZus Ontology
│   ├── ontology-addresses.ttl       <- Core part of the ontology to describe landmarks and addresses
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
├── LICENCE.md
└── README.md
```

### `data` folder

This folder stores files used to build knowledge graph. It is split in two repositories:
* `addresses` folder contains csv and geojson files which describe addresses and streets from different sources at different times (RDF resources are built during process) ;
* `land-registry` has RDF resources for the specific case of the plots from the Napoleonic land registry.

⚠️ To get more information about their content, please read their readme : [addresses](data/addresses/README.md) and [land-registry](data/land-registry/README.md)

### `ontology` folder
Two files describe the ontology: `ontology-addresses.ttl` is the core part of the ontology and describe landmarks and addresses whereas `ontology-land-registry.ttl` integrates specific modules used to describe the Napoleonic land registry documents and landmarks.

[Ontology documentation](ontology/documentation) is divided into as many parts as there are modelets:
* [`addresses`](ontology/documentation/addresses) with its extension for [land registry landmarks](ontology/documentation/addresses/land_registry_landmarks_extension) ;
* [`land_registry_documents_use`](ontology/documentation/land_registry_documents_use) ;
* [`sources`](ontology/documentation/sources) ;
* [`taxpayers`](ontology/documentation/taxpayers) ;
* [`temporal_evolution`](ontology/documentation/temporal_evolution).

Each modelet documentation has 3 or 4 files:
* `{modelet_name}_scenario.md`: the natural-language argument describing the sub-problem to be addressed ;
* `{modelet_name}_glossary.md`: glossary which defines the main terms involved ;
* `{modelet_name}_competency_questions.md`: set of informal competence questions (in natural language) which represent the questions to be answered by the knowledge base ;
* `{modelet_name}_sparql_queries.md`: it translates informal competence questions into SPARQL queries.
 
### `scripts` folder
This folder contains code to build knowledge graphs. Since addresses and land plots have their own specificities, each one has a folder in which its code allow KG construction.

⚠️ To get more information about their content, please read their readme : [addresses](scripts/addresses/README.md) and [land-registry](scripts/land-registry/README.md)

## Acknowledgements
This work was supported by the IGN and the AID.

## To cite this work
```
@inproceedings{bernard:hal-04721538,
  TITLE = {{PeGazUs: A knowledge graph based approach to build urban perpetual gazetteers}},
  AUTHOR = {Bernard, Charly and Tual, Solenn and Abadie, Nathalie and Dum{\'e}nieu, Bertrand and Perret, Julien and Chazalon, Joseph},
  URL = {https://hal.science/hal-04721538},
  BOOKTITLE = {{International Conference on Knowledge Engineering and Knowledge Management (EKAW 2024)}},
  ADDRESS = {Amsterdam, Netherlands},
  PUBLISHER = {{Springer Nature Switzerland}},
  SERIES = {Lecture Notes in Computer Science},
  VOLUME = {15370},
  PAGES = {364-381},
  YEAR = {2024},
  MONTH = Nov,
  DOI = {10.1007/978-3-031-77792-9\_22},
}
```