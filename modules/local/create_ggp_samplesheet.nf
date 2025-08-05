process CREATE_GGP_SAMPLESHEET {
    tag "${params.study_accession}"
    label 'process_single'

    conda "${moduleDir}/environment.yml"
    container "${workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container
        ? 'https://depot.galaxyproject.org/singularity/python:3.9--1'
        : 'biocontainers/python:3.9--1'}"

    input:
    path filtered_metadata
    val study_accession
    val outdir
    val library_strategy_filter

    output:
    path "ggp_samplesheet.csv", emit: samplesheet
    path "versions.yml",         emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def library_strategy_arg = library_strategy_filter ? "--library-strategy-filter ${library_strategy_filter}" : ""
    """
    create_ggp_samplesheet.py ${filtered_metadata} \\
        --study-accession ${study_accession} \\
        --outdir ${outdir} \\
        --output ggp_samplesheet.csv \\
        ${library_strategy_arg}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """

    stub:
    """
    touch ggp_samplesheet.csv
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}