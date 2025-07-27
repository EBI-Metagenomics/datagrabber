#!/usr/bin/env python3

import httpx
import sys
import logging
import argparse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def download_ena_metadata(study_accession, output_file="metadata.tsv"):
    """Download metadata from ENA API for the given study accession."""
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
    parser = argparse.ArgumentParser(description="Download ENA metadata")
    parser.add_argument("study_accession", help="ENA study accession (e.g., SRP493956)")
    parser.add_argument("--output", default="metadata.tsv", help="Output file name")

    args = parser.parse_args()

    download_ena_metadata(args.study_accession, args.output)


if __name__ == "__main__":
    main()
