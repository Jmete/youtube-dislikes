# This file helps test paths

import yaml
import os


def testpaths():

    print("Testing Paths")
    # Get the root path of directory structure
    try:
        ROOT_DIR = os.path.abspath(os.curdir)
        print(ROOT_DIR)
        print(f"ROOT_DIR type is {type(ROOT_DIR)}")
    except Exception as e:
        print("Error in root dir")
        print(e)

    # Try other relative paths
    try:
        INTERIM_PATH = os.path.join(ROOT_DIR, "data/interim")
        print(INTERIM_PATH)
        print(f"INTERIM_PATH type is {type(INTERIM_PATH)}")
    except Exception as e:
        print("Error in relative paths")
        print(e)

    # Get config yaml for path variable
    try:
        config_path = os.path.join(ROOT_DIR,"config.yml")
        config = yaml.safe_load(open(config_path))
        print(config.keys,config.items)
    except Exception as e:
        print("Error in yaml")
        print(e)

if __name__ == "__main__":
    testpaths()