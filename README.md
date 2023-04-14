* run  'make -f Makefile.mk to create some folders '
* Databse configuration file is saved in pyproject.toml file in the section 
* Plage de travail : fin du projet - début du projet 
* Durée d'écriture : n_modifs * 20






# How to run the project?

NB: In the following, we suppose that the ``Labnbook`` database and the ``versionning`` (of the form `id_report.gzip`)files are available in your local machine.

1. Create a prefect account following this [link](https://www.prefect.io/).
2. Configure prefect cloud following this [link](https://docs.prefect.io/latest/ui/cloud-local-environment/).
3. Run the following command line in your terminal in order to clone this git repository:
  
        Git clone https://github.com/anismhaddouche/Indicators.git
4. Past the `versionning` folder into the `data` folder.

5. Create a virtual env with conda. If conda is not installed, follow this [link](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) in order to install it.

        conda env create -f python_env.yml

6. Modifies these sections in the `pyproject.toml` file
   1. `database`: in order to connect to the database (which is assumed to be installed in your machine):

                user = "your_user"
                password = "your_password"
                host = "localhost"
                database_name  = "your_database_name"

   2. `missions`: choose if you want to run the project on all missions or only a subset.

                all = false # Choose all missions in the versioning folder
                subset =  ["1376","453","1559","1694","556","534","1640","1694","451","1237","533","647"]

7. In order tu run the all the flows, open a terminal, navigate to the repository `Indicators` and run the following commands:

        conda activate ml 
        python scripts/run_flows.py

8. Open prefect cloud in your browser in order to monitor the flows.
9. In order tu get some reports run this command:

        streamlit run scripts/dashboard.py