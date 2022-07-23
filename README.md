# Farmers Market Analysis
## CS513: Theory & Practice of Data Cleaning


## Setup


## Notebook to Python
    
    pip install nbconvert # if it's not installed
    jupyter nbconvert farmers_data_exploration.ipynb --to python


## Generate provenance

     java -jar yw.jar graph farmers_data_exploration.py >exp.gv
     dot -Tpng -o exp.gv