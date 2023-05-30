import os
import subprocess
import glob
import wandb
import random

# start a new wandb run to track this script
wandb.init(
    # set the wandb project where this run will be logged
    project="apa-lortia",
    dir="/mnt/e/Documents/Remote/lab/APA",
    # track hyperparameters and run metadata
    config={
        "model": "lortia",
        "dataset": "covid-nanopore",
        "working_dir": "/mnt/e/Documents/Remote/lab/APA",
        "sam_path": "/mnt/e/Documents/Remote/lab/APA/aln",
        "fa_file": "/mnt/e/Documents/APA/Homo_sapiens.GRCh38.cdna.all.fa",
        "gtf_file": "/mnt/e/Documents/APA/Homo_sapiens.GRCh38.109.gtf",
        "fq_files": "/mnt/e/Documents/APA/fastq/*.fastq",
        "lortia_path": "/mnt/e/Documents/Remote/lab/APA/LoRTIA/",
        "lortia_config": "-5 TGCCATTAGGCCGGG --five_score 16 --check_in_soft 15 -3 AAAAAAAAAAAAAAA --three_score 16 -s poisson -f True",
        "pychopper_config": "-U -y",
        "minimap2_config": "-ax splice",
    },
)

# Set variables from wandb configuration
wd = wandb.config["working_dir"]
sam_path = wandb.config["sam_path"]
fa_file = wandb.config["fa_file"]
gtf_file = wandb.config["gtf_file"]
fq_files = glob.glob(wandb.config["fq_files"])
lortia_path = wandb.config["lortia_path"]
chop_files = glob.glob(f"{wd}/chop/*_full.fq")


def run_pychopper(fq_files):
    subprocess.run(f"mkdir -p '{wd}/chop/'", shell=True)
    for fq in fq_files:
        # Extract sample names from files
        sample = os.path.splitext(fq)[0].split("/")[-1]
        subprocess.run(
            f"pychopper -U -y -r {wd}/chop/{sample}_report.pdf -u {wd}/chop/{sample}_unclassified.fq \
                -w {wd}/chop/{sample}_rescued.fq -S {wd}/chop/{sample}_stats.txt \
                    {fq} {wd}/chop/{sample}_full.fq",
            shell=True,
        )


# Run Minimap2
def run_minimap2(fq_files):
    # Make minimap2 output directory if it doesn't exist
    subprocess.run(f"mkdir -p '{wd}/aln/'", shell=True)
    for fq in fq_files:
        # Extract sample names from files
        sample = os.path.splitext(fq)[0].split("/")[-1]
        sam = sample + ".sam"
        if (
            glob.glob(f"{sam_path}/{sample}.sam") == []
        ):  # If sam file for sample doesn't exist
            subprocess.run(
                f"echo'Running minimap2' && minimap2 -ax splice {fa_file} {fq} > {wd}/aln/{sam} && \
                    echo 'Running samtools flagstat' && \
                    samtools flagstat {sam_path}/{sample}.sam > {sam_path}/{sample}.flagstat.txt",
                shell=True,
            )  # Run minimap2 and samtools flagstat
        else:  # If sam file for sample already exists only run samtools flagstat
            subprocess.run(
                f"samtools flagstat {sam_path}/{sample}.sam > {sam_path}/{sample}.flagstat.txt",
                shell=True,
            )


# Run LoRTIA
def run_script_on_sams(sam_path):
    sam_files = glob.glob(f"{sam_path}/*.sam")
    subprocess.run(f"mkdir -p '{wd}/lortia_results/'", shell=True)
    for sam in sam_files:
        # Run script on bam file
        subprocess.run(
            f"{lortia_path}/LoRTIA -5 TGCCATTAGGCCGGG --five_score 16 \
                       --check_in_soft 15 -3 AAAAAAAAAAAAAAA --three_score 16 -s poisson -f True \
                       {sam} {wd}/lortia_results/ \
                       {fa_file}",
            shell=True,
        )


class minimap_err(Exception):
    "Raised when minimap2 failed and there are no sam files"
    pass

run_pychopper(fq_files)

if glob.glob(f"{sam_path}/*.flagstat.txt") != []:  # If flagstat is already run
    print("Running LorTIA on existiing sam files")
    run_script_on_sams(sam_path)
else:
    try:
        run_minimap2(chop_files)
    except minimap_err:  # if minimap2 failed
        print("Failed to run minimap2")
    else:
        try:
            run_script_on_sams(sam_path)
        except:
            print("Failed to run LoRTIA")

wandb.finish()
