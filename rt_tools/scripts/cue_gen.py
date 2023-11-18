"""
Utility to generate rutracker classical music release from CUE files
"""
import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="+", help="Directory or CUE file to process")
    args = parser.parse_args()
    print(args)
    return 0