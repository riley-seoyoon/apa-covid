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
        "dataset": "covid-hepg2",
    },
)

wd = "/mnt/e/Documents/Remote/lab/APA"
# bam_file_path = "/Users/seoyoonpark/Library/CloudStorage/GoogleDrive-sypark217@eunbi.co.uk/Other computers/My computer/APA/A549/*.bam"
sam_file_path = f"{wd}/aln/*.sam"
transcriptome_file = "/mnt/e/Documents/APA/Homo_sapiens.GRCh38.cdna.all.fa"
gtf_file = "/mnt/e/Documents/APA/Homo_sapiens.GRCh38.109.gtf"
fq_files = glob.glob("/mnt/e/Documents/APA/fastq/*.fastq")
lortia_path = "/mnt/e/Documents/Remote/lab/APA/LoRTIA/"


# Run Minimap2
def run_minimap2(fq_files):
    subprocess.run(f"mkdir -p '{wd}/aln/'", shell=True)
    for fq in fq_files:
        sample = os.path.splitext(fq)[0].split("/")[-1]
        sam = sample + ".sam"
        # Run script on fq file
        subprocess.run(
            f"minimap2 -ax splice {transcriptome_file} {fq} > {wd}/aln/{sam}",
            shell=True,
        )


# Run LoRTIA
def run_script_on_sams(sam_file_path):
    sam_files = glob.glob(sam_file_path)
    subprocess.run(f"mkdir -p '{wd}/lortia_results/'", shell=True)
    for sam in sam_files:
        # Run script on bam file
        subprocess.run(
            f"{lortia_path}/LoRTIA -5 TGCCATTAGGCCGGG --five_score 16 \
                       --check_in_soft 15 -3 AAAAAAAAAAAAAAA --three_score 16 -s poisson -f True \
                       {sam} {wd}/lortia_results/ \
                       {transcriptome_file}",
            shell=True,
        )


class minimap_err(Exception):
    "Raised when minimap2 failed and there are no sam files"
    pass


try:
    run_minimap2(fq_files)
    if glob.glob(sam_file_path) == []:
        raise minimap_err
except minimap_err:
    subprocess.run(f"rmdir '{wd}/aln/'", shell=True)
    print("failed to run minimap2")
else:
    run_script_on_sams(sam_file_path)

wandb.finish()
