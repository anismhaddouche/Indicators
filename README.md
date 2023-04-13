* run  'make -f Makefile.mk to create some folders '
* Databse configuration file is saved in pyproject.toml file in the section 
* Plage de travail : fin du projet - début du projet 
* Durée d'écriture : n_modifs * 20






# Reproduire le projet 
NB : In the following, we suppose the labnbook database is installed locally in you machine and, also, the versionning files in the folder "data/versioning". 

* Clone this repository 
  
        Git clone https:///

* Create a virtuale env with conda. If conda is not installed, follow this [link](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) in order to install it.
            
        conda env create -f python_env.yml

* Modifies theses sections in the `pyproject.toml` file
  * `database`: in order to connect to the database (which is assumed to be installed in your machine)
        
        user = "your_user"
        password = "your_password"
        host = "localhost"
        database_name  = "your_database_name"

  * `missions`: choose if you want to run the project on all missions or only a subset 

        all = false # Choose all missions in the versioning folder
        subset =  ["1376","453","1559","1694","556","534","1640","1694","451","1237","533","647"]