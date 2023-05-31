#!/usr/bin/env python3

import subprocess
import glob
import os
import multiprocessing
from argparse import ArgumentParser
from functools import partial
import tqdm

def generate_toy_data(args):
    size, sam = args
    toy_path = "/mnt/e/Documents/Remote/lab/APA/apa-covid/toy_data"
    sample = os.path.splitext(sam)[0].split("/")[-1]
    generate_data = subprocess.run(
        f"samtools view -h --subsample-seed 42 -s {size} {sam} > {toy_path}/{sample}_sub.sam",
        shell=True,
    )
    print(f"{generate_data.args}")

def run_subsample(sam_path, size):
    sam_files = glob.glob(f"{sam_path}/*.sam")
    n_processes = 10
    pool = multiprocessing.Pool(n_processes)
    generate_partial = partial(generate_toy_data)
    results = []
    with tqdm.tqdm(total=len(sam_files)) as pbar:
        for result in pool.imap_unordered(generate_partial, ((size, sam) for sam in sam_files)):
            results.append(result)
            pbar.update()
    pool.close()
    pool.join()

def parsing():
    """
    This part handles the commandline arguments
    """
    parser = ArgumentParser(description="Subsample sam files")
    parser.add_argument("sam_path", type=str, help="Path to full sam files", metavar="sam_path")
    parser.add_argument("--size", type=float, help="Size of the subsample", default=0.1, metavar="size")
    return parser.parse_args()

if __name__ == "__main__":
    args = parsing()
    run_subsample(args.sam_path, args.size)
