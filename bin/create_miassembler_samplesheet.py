#!/usr/bin/env python3

import csv
import urllib.parse
import argparse
from pathlib import Path


def create_samplesheet(
    metadata_file,
    study_accession,
    assembler,
    memory,
    contaminant_reference,
    outdir,
    output_file="samplesheet.csv",
):
    """Create a samplesheet CSV with metadata for pipeline input.

    :param metadata_file: Path to the ENA metadata TSV file
    :param study_accession: ENA study accession
    :param assembler: Assembler to use for assembly
    :param memory: Memory allocation for assembly
    :param contaminant_reference: Contaminant reference file path
    :param outdir: Output directory path
    :param output_file: Output samplesheet file path
    """
    sample_data = []

    with open(metadata_file, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            run_accession = row["run_accession"]
            fastq_urls = row.get("fastq_ftp", "")
            library_layout = row.get("library_layout", "")
            library_source = row.get("library_source", "")
            library_strategy = row.get("library_strategy", "")
            platform = row.get("instrument_platform", "")

            if not fastq_urls or not fastq_urls.strip():
                continue

            urls = [url.strip() for url in fastq_urls.split(";") if url.strip()]

            # Determine file paths after download
            fastq_1 = ""
            fastq_2 = ""

            if len(urls) >= 1:
                parsed_url = urllib.parse.urlparse(urls[0])
                filename_1 = Path(parsed_url.path).name
                fastq_1 = f"{outdir}/{study_accession}/{run_accession}/{filename_1}"

            if len(urls) >= 2:
                parsed_url = urllib.parse.urlparse(urls[1])
                filename_2 = Path(parsed_url.path).name
                fastq_2 = f"{outdir}/{study_accession}/{run_accession}/{filename_2}"

            sample_data.append(
                {
                    "study_accession": study_accession,
                    "reads_accession": run_accession,
                    "fastq_1": fastq_1,
                    "fastq_2": fastq_2,
                    "library_layout": library_layout.lower(),
                    "library_source": library_source.lower(),
                    "library_strategy": library_strategy.lower(),
                    "platform": platform,
                    "assembler": assembler,
                    "assembly_memory": memory,
                    "assembler_config": "",
                    "contaminant_reference": contaminant_reference,
                    "human_reference": "",
                    "phix_reference": "",
                }
            )

    # Write CSV file
    with open(output_file, "w", newline="") as csvfile:
        if sample_data:
            fieldnames = sample_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)

    print(f"Created samplesheet with {len(sample_data)} samples")


def main():
    parser = argparse.ArgumentParser(
        description="Create samplesheet from filtered metadata"
    )
    parser.add_argument("metadata_file", help="Input metadata TSV file")
    parser.add_argument("--study-accession", required=True, help="Study accession")
    parser.add_argument("--assembler", default="metaspades", help="Assembler to use")
    parser.add_argument("--memory", default="350", help="Assembly memory setting")
    parser.add_argument(
        "--contaminant-reference", default="", help="Contaminant reference file"
    )
    parser.add_argument("--outdir", required=True, help="Output directory path")
    parser.add_argument(
        "--output", default="samplesheet.csv", help="Output samplesheet file"
    )

    args = parser.parse_args()

    create_samplesheet(
        args.metadata_file,
        args.study_accession,
        args.assembler,
        args.memory,
        args.contaminant_reference,
        args.outdir,
        args.output,
    )


if __name__ == "__main__":
    main()
