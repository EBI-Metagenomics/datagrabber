#!/usr/bin/env python3

import httpx
import sys
import logging
import argparse
import csv
from typing import Optional, Set

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def filter_metadata(
    input_file: str,
    output_file: str,
    library_strategy_filter: Optional[str] = None,
    run_accessions_filter: Optional[str] = None,
) -> None:
    """
    Filter the metadata TSV file based on library strategy and run accessions.
    
    :param input_file: Path to input TSV file
    :param output_file: Path to output filtered TSV file
    :param library_strategy_filter: Library strategy to exclude (case-insensitive)
    :param run_accessions_filter: Path to file with allowed run accessions (one per line)
    """
    allowed_runs: Optional[Set[str]] = None
    if run_accessions_filter:
        try:
            with open(run_accessions_filter, 'r') as f:
                allowed_runs = {line.strip() for line in f if line.strip()}
            logger.info(f"Loaded {len(allowed_runs)} allowed run accessions from {run_accessions_filter}")
        except FileNotFoundError:
            logger.error(f"Run accessions filter file not found: {run_accessions_filter}")
            sys.exit(1)
    
    filtered_count = 0
    total_count = 0
    
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile, delimiter='\t')
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames, delimiter='\t')
        writer.writeheader()
        
        for row in reader:
            total_count += 1
            
            # Apply run accessions filter if provided
            if allowed_runs and row['run_accession'] not in allowed_runs:
                logger.info(f"Skipping run {row['run_accession']} - not in allowed runs list")
                continue
                
            # Apply library strategy filter if provided
            if library_strategy_filter:
                library_strategy = row.get('library_strategy', '').lower()
                if library_strategy == library_strategy_filter.lower():
                    logger.info(f"Skipping sample {row['run_accession']} because library_strategy is {row.get('library_strategy')}")
                    continue
            
            # Skip if no FASTQ URLs
            fastq_urls = row.get('fastq_ftp', '').strip()
            if not fastq_urls:
                logger.info(f"No FASTQ URLs found for {row['run_accession']}, skipping")
                continue
                
            writer.writerow(row)
            filtered_count += 1
    
    logger.info(f"Filtered {total_count} rows to {filtered_count} rows")


def download_ena_metadata(study_accession, output_file="metadata.tsv"):
    """
    Download metadata from ENA API for the given study accession.
    
    :param study_accession: ENA study accession (e.g., SRP493956)
    :param output_file: Output file path
    """
    base_url = "https://www.ebi.ac.uk/ena/portal/api/filereport"
    params = {
        "accession": study_accession,
        "result": "read_run",
        "fields": "run_accession,library_layout,library_source,library_strategy,study_title,fastq_ftp,instrument_platform",
        "format": "tsv",
        "download": "true",
        "limit": "0",
    }

    logger.info(f"Downloading metadata for study {study_accession}")

    try:
        with httpx.Client() as client:
            response = client.get(base_url, params=params)
            response.raise_for_status()
            content = response.text

        with open(output_file, "w") as f:
            f.write(content)

        logger.info(f"Downloaded metadata for study {study_accession} to {output_file}")

    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error downloading metadata: {e.response.status_code} - {e.response.text}"
        )
        sys.exit(1)
    except httpx.RequestError as e:
        logger.error(f"Request error downloading metadata: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error downloading metadata: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Download and filter ENA metadata")
    parser.add_argument("study_accession", help="ENA study accession (e.g., SRP493956)")
    parser.add_argument("--output", default="metadata.tsv", help="Output file name")
    parser.add_argument("--library-strategy-filter", help="Library strategy to exclude (case-insensitive)")
    parser.add_argument("--run-accessions-filter", help="Path to file with allowed run accessions (one per line)")

    args = parser.parse_args()

    # Download metadata first
    raw_output = "raw_metadata.tsv" if (args.library_strategy_filter or args.run_accessions_filter) else args.output
    download_ena_metadata(args.study_accession, raw_output)
    
    # Apply filters if any are specified
    if args.library_strategy_filter or args.run_accessions_filter:
        filter_metadata(
            raw_output,
            args.output,
            args.library_strategy_filter,
            args.run_accessions_filter
        )
        # Clean up raw file if it's different from output
        if raw_output != args.output:
            import os
            os.remove(raw_output)
            logger.info(f"Removed temporary file {raw_output}")


if __name__ == "__main__":
    main()
