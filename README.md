# Farmers Market Analysis
## CS513: Theory & Practice of Data Cleaning

## Directory Structure

- SQLITE Database and DDL & DML files- [database](database)
- project Input & Output location details- [dataset](dataset)
- openrefine export files- [openrefine](openrefine)
- All usecases (U0, U1.1, U1.2) provenance- [provenance](provenance)
- Source code of project- [src](src)

## Setup tools
    brew install graphviz
    pip install nbconvert

## Notebook to Python
    
    jupyter nbconvert src/farmers_data_exploration_rahul.ipynb --to python

## Generate provenance
    
     java -jar provenance/yw.jar graph src/farmers_data_exploration_rahul.py >provenance/u0_u1.2.gv
     cat provenance/u0_u1.2.gv | dot -Tpng -o provenance/u0_u1.2.png