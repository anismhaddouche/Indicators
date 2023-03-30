from flow_0 import * 
from flow_1 import *
from flow_2 import * 
from flow_3 import * 


if __name__ == "__main__":
    with open("pyproject.toml", "r") as f:
        config = toml.loads(f.read())
    run_flow_0(config)
    run_flow_1(config)
    run_flow_2(config)
    run_flow_3(config)

    

