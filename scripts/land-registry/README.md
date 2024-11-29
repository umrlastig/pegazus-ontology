# README

This folder contains 4 markdown files with the SPARQL requests specialized to build the KG of land plots.

## Requirements
1. Create the initial named graphs as described in the *data/and-registry* folder of this repository.
2. Add the [Ric-O ontology](https://github.com/ICA-EGAD/RiC-O/tree/master/ontology/current-version) into dedicated named graph (or default named graph)

## Execution
The algorithm files have to be executed in the following order :
1. Custom functions
2. Sanity checks
3. Update initial data
4. Build KG

Requests in *3_Update_Initial_data.md* and *4_Build_KG.md* can be executed automatically using the *python* scripts into the *python* folder.

## Evaluation
SPARQL requests to answer the competency questions are in the *XXX_sparql_request.md* file of the */documentation/modelet_XXX* folder of this repository.