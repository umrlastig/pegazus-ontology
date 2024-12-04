# README

The scripts in this folder aims to automatically execute the create of the KG of plots. 
It executes the exact sames requests that are described in the *.md* files of the top folder.

## Requirements
* Install Graph DB
* Create a repository :
    * Choose OWL2-RL (Optimized) reasonner.
* Create a Python virtual environnement (tested with Python 3.10.0).
```bash
python -m venv .venv/pegazus_kg
```
* Install the required Python libraries using ```requirements.txt```

## Run
* ```00-load-rdf-tographdb.ipynb``` : create the initial named graphs with turtle files
* ```01-add-custom-functions.ipynb``` : add custom funcstions into the repository
* ```02-sanity-check.ipynb``` : just to remind to check the consistency of data
* ```03-update-initial-data.ipynb``` : update the initial resources with more properties
* ```04-build-kg.ipynb``` : build the final KG using PeGaZus method