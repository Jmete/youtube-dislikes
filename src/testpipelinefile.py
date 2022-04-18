# This file is a very basic file to test our pipeline.
import sys

def main(argv):
    print("test pipeline file successfully called")
    print(f"Test number: {argv[1]}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))