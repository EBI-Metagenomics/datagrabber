#!/usr/bin/env python3

import csv
import urllib.parse
import argparse
from pathlib import Path
from typing import Optional, Dict, List


def create_ggp_samplesheet(
    metadata_file: str, 
    study_accession: str, 
    outdir: str, 
    output_file: str = 'ggp_samplesheet.csv', 
    library_strategy_filter: Optional[str] = None
) -> None:
    """
    Create a GGP (genomes-generation pipeline) samplesheet CSV from ENA metadata.
    
    The GGP pipeline expects the following columns:
    - id: Row identifier
    - fastq_1: Path to first raw read file
    - fastq_2: Path to second raw read file
    - assembly_accession: Identifier for the assembly
    - assembly: File path to the contigs file
    - assembler: Tool and version used to produce the assembly (optional)
    
    Args:
        metadata_file: Input metadata TSV file from ENA
        study_accession: Study accession identifier
        outdir: Output directory path where files will be downloaded
        output_file: Output samplesheet filename
        library_strategy_filter: Library strategy to exclude from samplesheet
    """
    sample_data: List[Dict[str, str]] = []
    
    with open(metadata_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            run_accession = row['run_accession']
            fastq_urls = row.get('fastq_ftp', '')
            library_layout = row.get('library_layout', '')
            library_strategy = row.get('library_strategy', '')
            # Assembly-related fields from ENA metadata
            assembly_accession = row.get('assembly_accession', '')
            assembly_ftp = row.get('assembly_ftp', '')
            
            if not fastq_urls or not fastq_urls.strip():
                continue
            
            # Apply library strategy filter if provided
            if library_strategy_filter:
                filter_library_strategy = library_strategy_filter.lower()
                if library_strategy.lower() == filter_library_strategy:
                    continue
            
            urls = [url.strip() for url in fastq_urls.split(';') if url.strip()]
            
            # Determine FASTQ file paths after download
            fastq_1 = ""
            fastq_2 = ""
            
            if library_layout.lower() == 'paired' and len(urls) > 2:
                # Look for _1 and _2 paired files for paired-end data
                paired1 = next((url for url in urls if '_1.fastq' in url), None)
                paired2 = next((url for url in urls if '_2.fastq' in url), None)
                
                if paired1 and paired2:
                    filename_1 = Path(urllib.parse.urlparse(paired1).path).name
                    filename_2 = Path(urllib.parse.urlparse(paired2).path).name
                    fastq_1 = f"{outdir}/{study_accession}/{run_accession}/{filename_1}"
                    fastq_2 = f"{outdir}/{study_accession}/{run_accession}/{filename_2}"
                else:
                    # Fallback to first two files
                    if len(urls) >= 1:
                        filename_1 = Path(urllib.parse.urlparse(urls[0]).path).name
                        fastq_1 = f"{outdir}/{study_accession}/{run_accession}/{filename_1}"
                    if len(urls) >= 2:
                        filename_2 = Path(urllib.parse.urlparse(urls[1]).path).name
                        fastq_2 = f"{outdir}/{study_accession}/{run_accession}/{filename_2}"
            else:
                # For single-end or when pattern matching fails
                if len(urls) >= 1:
                    filename_1 = Path(urllib.parse.urlparse(urls[0]).path).name
                    fastq_1 = f"{outdir}/{study_accession}/{run_accession}/{filename_1}"
                if len(urls) >= 2:
                    filename_2 = Path(urllib.parse.urlparse(urls[1]).path).name
                    fastq_2 = f"{outdir}/{study_accession}/{run_accession}/{filename_2}"
            
            # Handle assembly files
            assembly_path = ""
            if assembly_ftp and assembly_ftp.strip():
                # Parse assembly FTP URL to get filename
                assembly_filename = Path(urllib.parse.urlparse(assembly_ftp).path).name
                assembly_path = f"{outdir}/{study_accession}/{assembly_accession}/{assembly_filename}"
            
            # Use run_accession as the ID for the row
            sample_id = run_accession
            
            sample_data.append({
                'id': sample_id,
                'fastq_1': fastq_1,
                'fastq_2': fastq_2,
                'assembly_accession': assembly_accession,
                'assembly': assembly_path,
                'assembler': ''  # Optional field, leave empty as we don't have this info from ENA
            })
    
    # Write CSV file
    fieldnames = ['id', 'fastq_1', 'fastq_2', 'assembly_accession', 'assembly', 'assembler']
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"Created GGP samplesheet with {len(sample_data)} samples")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Create GGP (genomes-generation pipeline) samplesheet from ENA metadata'
    )
    parser.add_argument('metadata_file', help='Input metadata TSV file')
    parser.add_argument('--study-accession', required=True, help='Study accession')
    parser.add_argument('--outdir', required=True, help='Output directory path')
    parser.add_argument('--output', default='ggp_samplesheet.csv', help='Output samplesheet file')
    parser.add_argument(
        '--library-strategy-filter', 
        help='Library strategy to exclude from samplesheet'
    )
    
    args = parser.parse_args()
    
    create_ggp_samplesheet(
        args.metadata_file,
        args.study_accession,
        args.outdir,
        args.output,
        args.library_strategy_filter
    )


if __name__ == "__main__":
    main()