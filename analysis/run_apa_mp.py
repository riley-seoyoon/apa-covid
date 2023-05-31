import os
import subprocess
import glob
import wandb
import multiprocessing
from about_time import about_time

# start a new wandb run to track this script
wandb.init(
    project="apa-lortia",
    dir="/mnt/e/Documents/Remote/lab/APA",
    config={
        "model": "modified-lortia",
        "dataset": "covid-nanopore",
        "working_dir": "/mnt/e/Documents/Remote/lab/APA/apa_mp",
        "sam_path": "/mnt/e/Documents/Remote/lab/APA/apa_mp/aln",
        "fa_file": "/mnt/e/Documents/APA/Homo_sapiens.GRCh38.cdna.all.fa",
        "fq_files": "/mnt/e/Documents/Remote/lab/APA/qc/*.fq",
        "lortia_path": "/mnt/e/Documents/Remote/lab/APA/apa-covid/analysis/lortia_mod",
        "test_sams": "/mnt/e/Documents/Remote/lab/APA/LoRTIA/test",
        "sub_path": "/mnt/e/Documents/Remote/lab/APA/apa-covid/toy_data",
        # ---- Tool commands ----
        "lortia_config": "-5 TGCCATTAGGCCGGG --five_score 16 --check_in_soft 15 -3 AAAAAAAAAAAAAAA --three_score 16 -s poisson -f True",
        "minimap2_config": "-ax splice -Y",
        "qc_config": "-q 10 -l 500",
    },
)

# Set variables from wandb configuration
wd = wandb.config["working_dir"]
if wandb.config["dataset"] == "test":
    sam_path = wandb.config["test_sams"]
elif wandb.config["dataset"] == "subsample-nanopore":
    sam_path = wandb.config["sub_path"]
else:
    sam_path = wandb.config["sam_path"]

fa_file = wandb.config["fa_file"]
fq_files = glob.glob(wandb.config["fq_files"])
lortia_path = wandb.config["lortia_path"]
lortia_config = wandb.config["lortia_config"]
minimap2_config = wandb.config["minimap2_config"]
qc_config = wandb.config["qc_config"]


# def run_qc(fq_files):
#     make_qcdir = subprocess.run(
#         f"mkdir -p '{wd}/qc/'",
#         shell=True,
#     )
#     print("{}".format(make_qcdir.args))
#     for fq in fq_files:
#         # Extract sample names from files
#         sample = os.path.splitext(fq)[0].split("/")[-1]
#         if glob.glob(f"{wd}/qc/{sample}/*.html") == []:
#             nanoqc = subprocess.run(
#                 f"nanoQC -o {wd}/qc/{sample} {fq} && \
#                            cat {fq} | chopper {qc_config} 2> {wd}/qc/{sample}_chopper.log > {wd}/qc/{sample}.fq",
#                 shell=True,
#             )
#             print("{}".format(nanoqc.args))
#         else:
#             if glob.glob(f"{wd}/qc/{sample}.fq") == []:
#                 chopper = subprocess.run(
#                     f"cat {fq} | chopper {qc_config} 2> {wd}/qc/{sample}_chopper.log > {wd}/qc/{sample}.fq",
#                     shell=True,
#                 )
#                 print("{}".format(chopper.args))
#             else:
#                 print(f"QC already run for {sample}")


def run_minimap2(fq_files):
    aln_dir = subprocess.run(
        f"mkdir -p '{wd}/aln/'",
        shell=True,
    )
    print("{}".format(aln_dir.args))
    for fq in fq_files:
        # Extract sample names from files
        sample = os.path.splitext(fq)[0].split("/")[-1]
        sam = sample + ".sam"
        if not os.path.exists(f"{sam_path}/{sample}.sam"):
            minimap2_flagstat = subprocess.run(
                f"echo 'Running minimap2 on {sample}' && minimap2 {minimap2_config} {fa_file} {fq} > {wd}/aln/{sam} && \
                    echo 'Running samtools flagstat on {sample}' && \
                    samtools flagstat {sam_path}/{sample}.sam > {sam_path}/{sample}.flagstat.txt",
                shell=True,
            )
            print("{}".format(minimap2_flagstat.args))
        else:
            minimap2_flagstat = subprocess.run(
                f"samtools flagstat {sam_path}/{sample}.sam > {sam_path}/{sample}.flagstat.txt",
                shell=True,
            )
            print("{}".format(minimap2_flagstat.args))


def run_lortia(sam_path):
    sam_files = glob.glob(f"{sam_path}/*.sam")
    for sam in sam_files:
        sample = os.path.splitext(sam)[0].split("/")[-1]    
        lortia_dir = subprocess.run(
        f"mkdir -p '{wd}/lortia_results_test/{sample}'",
        shell=True,
        )
        print("{}".format(lortia_dir.args))
        lortia_run = subprocess.run(
            f"{lortia_path}/__init__.py {lortia_config} {sam} {wd}/lortia_results/{sample}/ {fa_file}",
            shell=True,
        )
        print("{}".format(lortia_run.args))

# def process_sample_lortia(sam):
#     """
#     Process a single sample with LoRTIA.
#     """
#     sample = os.path.splitext(sam)[0].split("/")[-1]    
#     lortia_dir = subprocess.run(
#         f"mkdir -p '{wd}/lortia_results_test/{sample}'",
#         shell=True,
#     )
#     print("{}".format(lortia_dir.args))
#     lortia_run = subprocess.run(
#         f"{lortia_path}/LoRTIA {lortia_config} {sam} {wd}/lortia_results_test/{sample}/ {fa_file}",
#         shell=True,
#     )
#     print("{}".format(lortia_run.args))

# def run_lortia(sam_path):
#     sam_files = glob.glob(f"{sam_path}/*.sam")

#     # Modify the number of processes as needed
#     n_processes = 4

#     # Create a list of samples to process
#     samples_to_process = [(sam,) for sam in sam_files]

#     # Run the processing function in parallel for multiple samples
#     with multiprocessing.Pool(n_processes) as pool:
#         pool.starmap(process_sample_lortia, samples_to_process)

# run_qc(fq_files)
# run_minimap2(fq_files)
# with about_time() as t:
run_lortia(sam_path)
# print("Total running time for LoRTIA: {}".format(t.duration_human))

wandb.finish()
