#!/bin/bash

# Shell script to run our pipeline to download data, process it, and 
# export a trained machine learning model that can be used to classify 
# videos as negative, neutral, or positive. 

# Note: You may need to make the file executable.
# chmod +x runpipeline.sh
# Then you can simply run ./runpipeline.sh in your bash terminal.

# Exit script after first error
set -e

printf "Starting pipeline\n"
printf "This pipeline is intended to be run in a linux environment and uses bash commands. It also assumes some preconfiguration"
printf "Please make sure of the following:\n
Running in a linux env with a bash terminal\n
Miniconda is installed\n
postgres database is setup\n
config.yml is filled out\n\n"

# Detect if Conada is installed.
which conda || \
(printf "Error: Please install Miniconda\nhttps://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html\n" && exit 1)

# Create a new conda env to control our packages for the pipeline.
conda create --name "yd-mads-pipeline" python=3.8 pip

# Activate new env
source ~/miniconda3/etc/profile.d/conda.sh
conda activate yd-mads-pipeline

# Install packages from requirements.txt
pip install -r requirements.txt

# Install psycopg2 using conda since it often has trouble installing.
conda install psycopg2

# Get storage path
printf "Creating data storage folders."
STORAGE_PATH_TARS=$(cat config.yml | (shyaml get-value config.storepath))
echo "Storage path is $STORAGE_PATH_TARS"
printf "\n"
mkdir -p $STORAGE_PATH_TARS
mkdir -p data
mkdir -p data/external
mkdir -p data/interim
mkdir -p data/processed
mkdir -p data/raw

# Download tars from archive.org
printf '\nAbout to download tars from archive org
Be aware that this can take very long, and take up a lot of storage space.
We advise to skip this step and use the provided exports.\n'
printf "\nDo you want to run the download scripts? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) python src/data/downloadtars.py; break;;
        No ) break;;
    esac
done

printf "\n"

# Unzip tar files into folders of json files.

printf "We can attempt to untar the files automatically."
printf "\nDo you want to extract the tar files? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) find $STORAGE_PATH_TARS -type f -name "*.tar" -exec tar -xvf "{}" --skip-old-files --directory $STORAGE_PATH_TARS \;; break;;
        No ) break;;
    esac
done

printf "\n"

# Combine JSON files into larger Parquet files.
printf "The next step involves combining json files into larger parquet files. This can take a long time."
printf "\nDo you want to combine the json files into parquet files? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) python src/data/combinejson.py; break;;
        No ) break;;
    esac
done

printf "\n"

printf "Downloading and installing postgresql-client..."
sudo apt-get install postgresql-client

# Get database info from config
printf "\nGetting database config information."
DB_IP=$(cat config.yml | (shyaml get-value config.dbip))
DB_NAME=$(cat config.yml | (shyaml get-value config.dbname))
DB_USER=$(cat config.yml | (shyaml get-value config.dbuser))
DB_PORT=$(cat config.yml | (shyaml get-value config.dbport))
DB_PW=$(cat config.yml | (shyaml get-value config.dbpw))
DB_VIDEOTABLE=$(cat config.yml | (shyaml get-value config.dbvideotable))


# Create Database
printf "\nDo you want to create the database? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) PGPASSWORD=$DB_PW psql -h $DB_IP -d $DB_NAME -U $DB_USER -p $DB_PORT -a -q -f src/data/create_database.sql; break;;
        No ) break;;
    esac
done

# Create video_data table
printf "\nDo you want to create the video_data table in the database? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) PGPASSWORD=$DB_PW psql -h $DB_IP -d $DB_NAME -U $DB_USER -p $DB_PORT -a -q -f src/data/create_video_table.sql; break;;
        No ) break;;
    esac
done

# Load parquet file data into postgres database. File naturally checks if should proceed.
printf "\nThe next step involves loading data from the parquet files into the database. This can take a long time.\n"
printf "\nDo you want to start loading data into the database? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) python src/data/dataentry_from_parq.py; break;;
        No ) break;;
    esac
done

# Optimize the DB
printf "\nThe next step involves optimizing our database by creating indexes and performing ANALYZE on the table. This can take a long time.\n"
printf "\nDo you want to start optimizing the database? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) PGPASSWORD=$DB_PW psql -h $DB_IP -d $DB_NAME -U $DB_USER -p $DB_PORT -a -q -f src/data/optimizedb.sql ; break;;
        No ) break;;
    esac
done

# Export pickle of statistics of the full database as a whole as well as grouped by category.
printf "\nThe next step will export 2 pickle files of overall statistics of the database. This can take some time.\n"
printf "\nDo you want to start exporting the statistics pickles? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) python src/visualization/fulldb_stats.py ; break;;
        No ) break;;
    esac
done

# Export CSV files
printf "\nThe next step will export CSV files from the database. This can take a long time.\n"
printf "\nDo you want to start exporting the csv files? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) PGPASSWORD=$DB_PW psql -h $DB_IP -d $DB_NAME -U $DB_USER -p $DB_PORT -a -q -f src/data/psql_export_csv.sql ; break;;
        No ) break;;
    esac
done

# Download comment data.
printf "\nThe next step involves downloading comment data. This can take a long time.\n"
printf "\nDo you want to start downloading the comment data for most_liked_500000.csv? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        # You can change the arguments to resume paused downloads. Check the file for more details.
        Yes ) python src/data/download_main_args_inputfile.py 0 y most_liked_500000.csv ; break;;
        No ) break;;
    esac
done

printf "\nDo you want to start downloading the comment data for most_disliked_500000.csv? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        # You can change the arguments to resume paused downloads. Check the file for more details.
        Yes ) python src/data/download_main_args_inputfile.py 0 y most_disliked_500000.csv ; break;;
        No ) break;;
    esac
done

printf "\nDo you want to start downloading the comment data for random_percent_1.csv? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        # You can change the arguments to resume paused downloads. Check the file for more details.
        Yes ) python src/data/download_main_args_inputfile.py 0 y random_percent_1.csv ; break;;
        No ) break;;
    esac
done

printf "\nDo you want to start downloading the comment data for random_percent_point2.csv? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        # You can change the arguments to resume paused downloads. Check the file for more details.
        Yes ) python src/data/download_main_args_inputfile.py 0 y random_percent_point2.csv ; break;;
        No ) break;;
    esac
done

printf "\n"

printf "\nThe next step will process our csv files into training and testing dataframes.\n"
printf "\nDo you want to start creating the training and testing dataframes? [Select number below]\n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) python src/features/data_prep_for_model.py ; break;;
        No ) break;;
    esac
done

printf "\n"

printf "\n The next step will train our Random Forest model and export it as a pickle file. \n"
printf "\n Do you want to start training and exporting the model? [Select number below] \n"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) python src/models/train_model.py ; break;;
        No ) break;;
    esac
done

printf "\nPipeline finished."
