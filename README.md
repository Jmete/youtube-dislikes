# youtube-dislikes
University of Michigan - MADS - Capstone Project - Analysis and Prediction of dislikes on Youtube data

# Team Members
- James Mete (jmete)
- Jenna Mekled (jmekled)
- Sashaank Sekar (sashaank)

# Introduction
Dislike counts on Youtube videos are a useful signal for separating high quality videos from low quality videos or even potential scams. Youtube has recently removed the ability to see dislike count data publicly, and have disabled dislike count data in their API. Thus, our project seeks to understand the trends that influence dislike activity through analytical research and use those insights to generate a machine learning model to predict dislike counts or ratios to help alert users to potentially problematic videos based on the available data and features.

# Dataset
Since Youtube has removed the ability to actively scrape or query dislike counts, we have to rely on historical data to conduct our research. Luckily, extensive historical records have been kept by Archive.org, and we will use one called “Youtube Metadata Collection (2019-02)” (https://archive.org/details/Youtube_metadata_02_2019) which consists of around 1.46 Billion JSON records related to youtube metadata such as title, upload date, category, likes, dislikes, language, recommended videos, and other features. This is composed of around 5000 .tar files each with around 146 .json.gz files inside them which will require extensive data processing to download the files, process them, and store the data for future analysis. 

Our processing techniques will involve taking a sample of the full dataset (every fifth file) as well as removing potential NaN / Errors in calculated fields such as the like_dislike_ratio. The end result is a dataset of <b>80,910,144 rows</b>. We can conduct large-scale analysis using SQL commands over the full dataset.

We will complement this dataset with scraped comments of top videos (based on view count) to both add an element of NLP analysis which may also be a useful signal towards predicting whether or not a video may have a high number of dislikes.

Finally, we will be exporting smaller CSVs that are more useful for deeper analysis such as:
- Exporting the top 500,000 most disliked rows based on dislike_like_ratio
- Exporting the top 500,000 most liked rows based on dislike_like ratio
- Exporting a 1% random sample resulting in over 800,000 rows.

# Setup

## Our Machine
While we are performing experimentation and development on personal machines, our main production environment for running the full analysis code is the following:
- Linux (Pop!_OS 21.10, Based on Ubuntu)
- 64-bit operating system
- 73.1 GB RAM
- 6 Cores / 12 Threads
- Nvidia GeForce 3060 12GB VRAM
- PostgreSQL V14.2 (Debian 14.2-1.pgdg110+1) Installed via host machine

This is running as a KVM virtual machine inside a host server with the following specs:
- Intel Core i9-7940X CPU @ 3.10 GHz
- 128 GB RAM
- Linux (Unraid)

## Setting up your environment
We have used conda as an environment manager starting with the <b>rapids-ai template environment</b> (https://rapids.ai/start.html) which allows us access to gpu enabled processing libraries such as cuDF. We then add on to that environment with other needed packages as detailed in the <b>requirements.txt</b> file.

### Important packages & libraries include:
- Rapids AI suite (cuDF)
- Pandas
- Numpy
- SQLAlchemy
- PSYCOPG2
- Glob
- OS
- Plotly

## Setting up the database
PostgreSQL V14.2.
### Installing postgresql
In our case, this was installed through our host OS (unraid) which has a useful docker interface. However, any postgres environment will be suitable. Installing postgressql can differ depending on your environment, but a helpful tutorial is located here: https://www.postgresql.org/docs/14/tutorial-install.html

Furthermore, download options can be found here: https://www.postgresql.org/download/

For Ubuntu specifically:
https://www.postgresql.org/download/linux/ubuntu/

### Logging into the database

All mentioned database related scripts and commands in this section were run by logging into the database through psql which you can install on your local machine and connect remotely to the database. More information can be found here: https://www.postgresql.org/docs/14/app-psql.html

### Setting up the database and table

We set up our initial database through a UI installed through our host machine called "Adminer" (version 4.8.1). However, we have provided a SQL script to create the database as well in "create_database.sql". This will create a database called "youtube-dislikes".

Next, we create the table that will store our video data. Running the "create_video_table.sql" command through psql will drop the table if it already exists, then creates it as a fresh table with the appropirate schema.

## Setting up the config.yml file
Inside our repo is a config.yml-example file. This file is meant to be edited with various variables relevant to your system such as the storage path of where to save / load the dataset from, as well as security passwords which need to be kept safe. 

After editing the file as detailed inside the template, you should rename it to "config.yml" which will allow it to be accessed by future scripts in the project.

# Processing Steps

<span style="color:RED">NOTE: If you are interested in running these scripts, we HIGHLY suggest you skip the data download and processing steps due to the massive size, hardware requirements, and overall long processing times! Utilizing processed data such as the provided .csv files is preferred for analysis purposes.</span>

## Downloading the dataset
As mentioned previously, we will use a historical dataset called “Youtube Metadata Collection (2019-02)” which is located at https://archive.org/details/Youtube_metadata_02_2019

Running the <b>downloadtars.py</b> file allows the users to incrementally download the .tar files from archive.org. The script monitors the storagepath folder to check for downloaded files and skips them if detected. This helps if the script fails during procsesing and needs to be restarted.

We highly suggest using a NAS (network attached storage) for this since the massive dataset can be hundreds of GB in size. 

## Processing JSON
Running <b>combinejson.py</b> will go to the storagepath location, and process json files in batches by loading a user-specificed amount (which should be set depending on your memory capacity) into Pandas, and then exports the data into parquet files in a parq folder inside the storagepath location.

Doing so allows us to reduce over 140,000 JSON files into 301 Parquet files (each ~1,000,000 rows of data). While this adds an extremely lengthy processing step instead of directly going from JSON -> PostgreSQL, we found that pre-processing into parquet files can help with initial analysis and reduce IO bottlenecks later on when loading data into PostgreSQL.

<b>Note:</b> combinejson.py will create .pickle files it will use to store which paths it has already processed which will enable it to skip already processed files which helps if it ever gets stopped before completion.

## Loading data into PostgreSQL

Running <b>dataentry_from_parquet.py</b> will loop through the stored parquet files based on the storagepath variable (where combinejson.py saved them), performs some initial data cleaning and processing, arranges and renames the columns in the same order/name as the PostgreSQL table schema expects, and then loads the data into the database table.

Data processing steps performed at this step include:
- Converting date columns to datetime format.
- Converting dicts to json string objects that is suitable to be imported into PostgreSQL for a JSONB formatted column.
- Calculates initial ratios including view_like_ratio, view_dislike_ratio, and like_dislike_ratio
- Drops INF and NaN rows for the like_dislike_ratio to reduce dataset size and potential errors later on. We mainly only care about videos that actually have dislikes.
- Rename and Reorder columns to match database table schema.
- Loads data into PostgreSQL using batch importing utilizing the pd.to_sql command with multi mode enabled and a chunksize of 10,000 as default.

<b>Note:</b> dataentry_from_parquet.py will create .pickle files it will use to store which paths it has already processed which will enable it to skip already processed files which helps if it ever gets stopped before completion.

<b>Note:</b> After initial investigation, we decided to go with dislike_like_ratio, although this is not present in the script. This is because it is included as a calcualated column in PostgreSQL itself. Furthermore, we used a normalization technique of adding 1 to the numerator and denominator to avoid any 0 division errors as well as avoiding too many rows simply being 0 (due to 0/X = 0). This column is a major focal point of our research since it allows us to sort the database by the dislike_like_ratio as well as determine roughly how problematic a video is. However, we will not be able to calculate this in a real-life situation due to the dislike data being hidden which is a future challenge. Thus, we must find suitable proxies during our analysis stage.

# Analysis Steps

### TO DO


