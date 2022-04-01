# This file is a wrapper to download files from the internet archive.
# It is specifically coded to download files from the youtube 2019-02, 
# but could be adapted to other archives with some simple adjustments to the tar file names.

# Iterates through urls and downloads tars
# Example url is https://archive.org/download/Youtube_metadata_02_2019/0000.tar

# Based on code from stack overflow

import wget
import glob
import ssl
import yaml
import os

ROOT_DIR = os.path.abspath(os.curdir)
config_path = os.path.join(ROOT_DIR,"config.yml")


def downloadtars():

    # Get config yaml for path variable
    config = yaml.safe_load(open(config_path))

    #get past certificate verified failed issue
    ssl._create_default_https_context = ssl._create_unverified_context

    print('Beginning file downloads with wget module')
    numfiles = 5000
    baseurl = "https://archive.org/download/Youtube_metadata_02_2019/"
    storelocation = config["config"]["storepath"]
    print(f"Store Location is: {storelocation}")

    # Check for existing files so we don't redownload the same files
    existing_file_paths = glob.glob(storelocation+"*.tar")
    existing_files = [f[-8:-4] for f in existing_file_paths]
    print(existing_files)

    for i in range(numfiles):
        # Due to the enormous amount of data, we will only download every 5th file to get a more diverse but large dataset
        if i % 5 == 0:
            filenumber = str(i).zfill(4)
            print(filenumber)
            if filenumber not in existing_files:
                durl = baseurl + filenumber + ".tar"
                print(f"Downloading {durl}")
                fileurl = storelocation + filenumber + ".tar"
                wget.download(durl, fileurl)
                print(f"Finished downloading {filenumber}")

    print("Finished downloading")

if __name__ == "__main__":
    downloadtars()