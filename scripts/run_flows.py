
from prefect import variables
from prefect import flow
from flow_0 import * 
from flow_1 import *
from flow_2 import * 
from flow_3 import * 

@flow()
def run_flows(all:bool=False, subset:list=["1376","453","1559","1694","556","534","1640","1694","451","1237","533","647"]
              ):
 
    if not 'path_for_flow_1' in locals():
        path_for_flow_1 = "data/tmp/0_missions_texts"
    if not 'path_for_flow_2' in locals():
        path_for_flow_2 = "data/tmp/1_missions_contribs"
    if not 'path_1_for_flow_3' in locals():
        path_1_for_flow_3 = "data/tmp/2_collab.json.gz"
    if not 'path_2_for_flow_3' in locals():
        path_2_for_flow_3 = "data/tmp/2_semantic.json"
    
    with open("pyproject.toml", "r") as f:
        config = toml.loads(f.read())
    config['missions']['all'] = all
    if all == False :
        config['missions']['subset'] = subset

    path_for_flow_1 = run_flow_0(config)
    path_for_flow_2 = run_flow_1(config, path_for_flow_1)
    path_1_for_flow_3,  path_2_for_flow_3 = run_flow_2(config, path_for_flow_2)
    run_flow_3(config,path_1_for_flow_3,  path_2_for_flow_3)

    

if __name__ == "__main__":
        run_flows()


