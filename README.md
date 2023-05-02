<!-- * run  'make -f Makefile.mk to create some folders '
* Databse configuration file is saved in pyproject.toml file in the section 
* Plage de travail : fin du projet - début du projet 
* Durée d'écriture : n_modifs * 20/30 -->

# How to run the project?

*NB: In the following, we suppose that the ``LabNbook`` database and the ``versionning`` (of the form `id_report.gzip`) files are available in your local machine. Note that, the project can be run without the `Prefect` orchestrator. It can be down by removing is all flows the `Prefect` tags (`@task, @flow and @logger`) and ignoring steps 1 and 2.*

1. Create a Prefect account following this [link](https://www.prefect.io/).
2. Configure Prefect cloud following this [link](https://docs.prefect.io/latest/ui/cloud-local-environment/).
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

8. Open `Prefect` (cloud) in your browser in order to monitor the flows or run it locally with

        prefect server start 

9. In order tu get some reports run this command:

        streamlit run scripts/dashboard.py

# Flows description

## Flow_0

The purpose of this flow is to connect to the previously installed `LabNbook` database and prepare `LabDocs` for the next flow which consists of calculating  contribution matrices.

### Tasks (Flow_0)

* `extract_text_init`

  * Dependencies
    * The dictionary `[database]`in the `project.toml`file.
  * Returns
    * The file `data/tmp/0_labdocs_texts_init.json.gz`

* `extract_text`

* Dependencies:
  * The dictionary `[regex_text_patterns]` in the `project.toml`file.
* Returns:
  * The folder `data/tmp/0_missions_texts`

## Flow_1

The purpose of this flow is to calculate contribution matrices and some variables that describes `LabDocs` as the number of tokens, segments, ... etc.

### Tasks (Flow_1)

* `contrib_and_segmentation`
  * Dependencies
    * The folder `data/tmp/0_missions_texts`
    * The nlp model the config section `["nlp"]["spacy_model"]` of the file `project.toml`
  * Returns
    * The folder `data/tmp/1_missions_contrib`

## Flow_2

The purpose of this flow is to calculate all indicators.

### Tasks (Flow_2)

* `nonsemantic_indicator`
  * Dependencies
    * The dictionary `["missions"]` in `project.toml`file
  * Returns
    * The file `data/tmp/2_collab.json.gz`
  
* `semantic_indicators`
  * Dependencies
    * The two dictionary `["nlp"]["model"]` and `["missions"]` in the `project.toml` file
    * The nlp model in the config section `[config_nlp]` of the file `project.toml`
  * Returns
    * The file `data/tmp/reports/2_semantic.json`

## Flow_3

The purpose of this flow is to generate some reports.

### Tasks (Flow_3)

* `summary_nonsemantic_indicators_csv`
  * Dependencies
    * The file `data/tmp/2_collab.json.gz`
  * Returns
    * The file `data/tmp/reports/3_summary_nonsemantic_indicators.csv` and its corresponding Pandas DataFrame `df_nonsemantic`
  
* `semantic_indicator_csv`
  * Dependencies
    * The file `data/tmp/reports/2_semantic.json`
  * Returns
    * The file `data/tmp/reports/3_summary_semantic_indicator.csv` and its corresponding Pandas DataFrame `df_semantic`
  
* `get_times`
  * Dependencies
    * The file Pandas DataFrames `df_nonsemantic` and `df_semantic`
  * Returns
    * The file `data/tmp/reports/3_times.csv`

# How to improve this work

Besides the improvements concerning the quality of the python code, I propose two major improvements paths. The first one concern the nlp model in `scripts/utils/fr_LabnbookNer-0.0.0` used in the task `contrib_and_segmentation` of `flow_1.py`. The second one is the model `"all-MiniLM-L6-v2"` used in the task `semantic_indicator` of the `flow_2.py`. We give below some suggestions in order to improve these two models.