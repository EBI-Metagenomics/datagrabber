# ebi-metagenomics/datagrabber

## Project Overview

ebi-metagenomics/datagrabber is a Nextflow pipeline for downloading reads and assemblies from the European Nucleotide Archive (ENA). It automates the process of fetching metadata and FASTQ files for entire studies, and generates samplesheets for downstream MGnify pipelines like miassembler.

## Key Features

- Downloads ENA metadata for a specified study accession
- Filters samples based on library strategy (optional)
- Downloads FASTQ files for all valid samples
- Generates formatted samplesheets for downstream MGnify pipelines
  - For the metagenomics assembly pipeline (miassembler)

## Technologies Used

- Nextflow (DSL2, >=23.04.0)
- Docker/Singularity/Conda for containerization
- Python

## Instructions for Claude
- Always use nf-core coding style
- Prioritize simple and readable code
- Always avoid code repetition
- Add python RST like docstrings on methods