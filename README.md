# APA

## Project Overview

Alternative Polyadenylation (APA) analysis for long-read Nanopore COVID-19 data

## Source Data
A multi-omics investigation of the composition and function of extracellular vesicles along the temporal trajectory of COVID-19 ([link](https://www.nature.com/articles/s42255-021-00425-4))

GEO accession: [GSE174668](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174668)

## Analysis Workflow

### 1. Quality Control
[pychopper](https://github.com/epi2me-labs/pychopper)

### 2. Alignment

[minimap2](https://github.com/lh3/minimap2)

### 3. Identification of APA events

[LorTIA](https://github.com/zsolt-balazs/LoRTIA)

### 4. Differential analysis of APA

In-house mthod based on [DaPars2](https://github.com/3UTR/DaPars2)

Dependencies listed in requirements.txt