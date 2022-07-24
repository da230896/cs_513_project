# Farmers Market Analysis
## CS513: Theory & Practice of Data Cleaning


## Setup tools
    brew install graphviz
    pip install nbconvert

## Notebook to Python
    
    jupyter nbconvert src/farmers_data_exploration_rahul.ipynb --to python

## Generate provenance
    
     java -jar provenance/yw.jar graph src/farmers_data_exploration_rahul.py >provenance/provenance_u1.2.gv
     cat provenance/provenance_u1.2.gv | dot -Tpng -o provenance/provenance_u1.2.png