process DOWNLOAD_FASTQ {
    tag "$meta.run_accession"
    label 'process_medium'


    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/wget:1.21.4' :
        'biocontainers/wget:1.21.4' }"

    input:
    tuple val(meta), val(fastq1), val(fastq2)

    output:
    tuple val(meta), path("*.fastq.gz"), emit: fastq_files
    path "download_log.txt" , emit: download_log
    path "versions.yml"     , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    # Create download log
    echo "Downloading FASTQ files for ${meta.run_accession}" > download_log.txt
    
    # Download first FASTQ file
    echo "Downloading ${fastq1}" >> download_log.txt
    if wget -q '${fastq1}'; then
        echo "SUCCESS: Downloaded \$(basename '${fastq1}')" >> download_log.txt
    else
        echo "FAILED: Could not download ${fastq1}" >> download_log.txt
        exit 1
    fi
    
    # Download second FASTQ file if present (paired-end)
    if [ -n "${fastq2}" ] && [ "${fastq2}" != "null" ]; then
        echo "Downloading ${fastq2}" >> download_log.txt
        if wget -q '${fastq2}'; then
            echo "SUCCESS: Downloaded \$(basename '${fastq2}')" >> download_log.txt
        else
            echo "FAILED: Could not download ${fastq2}" >> download_log.txt
            exit 1
        fi
    fi
    
    echo "All downloads completed for ${meta.run_accession}" >> download_log.txt

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        wget: \$(wget --version | head -n1 | sed 's/GNU Wget //g')
    END_VERSIONS
    """

    stub:
    """
    touch test_1.fastq.gz
    touch test_2.fastq.gz
    touch download_log.txt
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        wget: \$(wget --version | head -n1 | sed 's/GNU Wget //g')
    END_VERSIONS
    """
}