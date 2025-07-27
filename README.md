# ebi-metagenomics/datagrabber

[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A523.04.0-23aa62.svg)](https://www.nextflow.io/)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)

## Introduction

**ebi-metagenomics/datagrabber** is a Nextflow pipeline for downloading reads and assemblies from the European Nucleotide Archive (ENA). It automates the process of fetching metadata and FASTQ files for entire studies, and generates samplesheets for downstream MGnify pipelines like miassembler.

The pipeline performs the following steps:

1. Downloads ENA metadata for a specified study accession
2. Filters samples based on library strategy (optional)
3. Downloads FASTQ files for all valid samples
4. Generates formatted samplesheets for downstream MGnify pipelines

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

To run the pipeline, you need to provide an ENA study accession:

```bash
nextflow run ebi-metagenomics/datagrabber \
    --study_accession SRP062869 \
    --outdir results \
    -profile docker
```

For more detailed usage instructions, see [docs/usage.md](docs/usage.md).

## Pipeline output

For details about the output files and reports, see [docs/output.md](docs/output.md).

## Quick Start

1. Install [`Nextflow`](https://www.nextflow.io/docs/latest/getstarted.html#installation) (`>=23.04.0`)

2. Install any of [`Docker`](https://docs.docker.com/engine/installation/), [`Singularity`](https://www.sylabs.io/guides/3.0/user-guide/) (you can follow [this tutorial](https://singularity-tutorial.github.io/01-installation/)), [`Podman`](https://podman.io/), [`Shifter`](https://nersc.gitlab.io/development/shifter/how-to-use/) or [`Charliecloud`](https://hpc.github.io/charliecloud/) for full pipeline reproducibility _(you can use [`Conda`](https://conda.io/miniconda.html) both to install Nextflow itself and also to manage software within pipelines. Please only use it within pipelines as a last resort; see [docs](https://nf-co.re/usage/configuration#basic-configuration-profiles))_.

3. Download the pipeline and test it on a minimal dataset with a single command:

   ```bash
   nextflow run ebi-metagenomics/datagrabber -profile test,docker --outdir <OUTDIR>
   ```

4. Start running your own analysis!

   ```bash
   nextflow run ebi-metagenomics/datagrabber \
       --study_accession <ENA_STUDY_ACCESSION> \
       --outdir <OUTDIR> \
       -profile docker
   ```

## Parameters

### Required parameters

- `--study_accession`: ENA study accession (e.g., SRP493956, PRJNA123456)
- `--outdir`: Output directory for results

### Optional parameters

- `--library_strategy_filter`: Library strategy to exclude from downloads (e.g., AMPLICON)
- `--samplesheet_format`: Format of output samplesheet (default: miassembler)
- `--assembler`: Assembler to use for miassembler pipeline (default: metaspades)
- `--memory`: Memory allocation for assembly process in GB (default: 350)
- `--contaminant_reference`: Path to contaminant reference file

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

## Credits

ebi-metagenomics/datagrabber was originally written by Martin Beracochea.

We thank the following people for their extensive assistance in the development of this pipeline:

<!-- TODO nf-core: If applicable, make list of people who have also contributed -->

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

## Citations

If you use ebi-metagenomics/datagrabber for your analysis, please cite it using the following doi: TBD

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

This pipeline uses code and infrastructure developed and maintained by the [nf-core](https://nf-co.re) community, reused here under the [MIT license](https://github.com/nf-core/tools/blob/main/LICENSE).

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).
