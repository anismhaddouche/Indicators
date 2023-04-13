* run  'make -f Makefile.mk to create some folders '
* Databse configuration file is saved in pyproject.toml file in the section 
* Plage de travail : fin du projet - début du projet 
* Durée d'écriture : n_modifs * 20






# How to run the project?

NB : In the following, we suppose the labnbook database is installed locally in you machine and, also, the versionning files in the folder "data/versioning". 

1. Create a prefect account following this [link](https://www.prefect.io/)
2. Configure prefect cloud following this [link](https://docs.prefect.io/latest/ui/cloud-local-environment/).
3. Clone this repository:
  
        Git clone https://github.com/anismhaddouche/Indicators.git

4. Create a virtual env with conda. If conda is not installed, follow this [link](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) in order to install it.

        conda env create -f python_env.yml

5. Modifies these sections in the `pyproject.toml` file
   1. `database`: in order to connect to the database (which is assumed to be installed in your machine):

                user = "your_user"
                password = "your_password"
                host = "localhost"
                database_name  = "your_database_name"

   2. `missions`: choose if you want to run the project on all missions or only a subset.

                all = false # Choose all missions in the versioning folder
                subset =  ["1376","453","1559","1694","556","534","1640","1694","451","1237","533","647"]

6. In order tu run the all the flows, open a terminal, navigate to the repository `ìndicators` and run the following commands:

        conda activate ml && python scripts/run_flows.py

7. Open prefect cloud in your browser in order to monitor the flows.
8. In order tu get some reports run this commande:

        streamlit run scripts/dashboard.py