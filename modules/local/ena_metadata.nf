process ENA_METADATA {

    tag "${study_accession}"

    label 'process_single'

    conda "${moduleDir}/environment.yml"
    container "${workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container
        ? 'oras://community.wave.seqera.io/library/httpx:0.28.1--a2d429ff2cc5f04d'
        : 'community.wave.seqera.io/library/httpx:0.28.1--71656cfc47f8950c'}"

    input:
    val study_accession

    output:
    path ("ena_metadata.tsv"), emit: metadata
    path "versions.yml",       emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    """
    ena_metadata.py ${study_accession} ${args} --output ena_metadata.tsv

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """

    stub:
    """
    touch ena_metadata.tsv
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
