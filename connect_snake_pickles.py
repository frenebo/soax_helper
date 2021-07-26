import argparse
import os
import pickle
from colorama import init, Fore, Back,Style

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('source_dir',help="Directory with snake pickles")
    parser.add_argument('target_dir',help="Directory to save pickled snakes")

    args = parser.parse_args()

