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
* 
