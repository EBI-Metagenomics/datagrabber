/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { paramsSummaryMap               } from 'plugin/nf-schema'
include { softwareVersionsToYAML         } from '../subworkflows/nf-core/utils_nfcore_pipeline'
include { ENA_METADATA                   } from '../modules/local/ena_metadata'
include { DOWNLOAD_FASTQ                 } from '../modules/local/download_fastq'
include { CREATE_MIASSEMBLER_SAMPLESHEET } from '../modules/local/create_miassembler_samplesheet'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow DATAGRABBER {
    take:
    ch_samplesheet // channel: samplesheet read in from --input

    main:

    ch_versions = Channel.empty()

    // Parameter validation is handled by nf-schema plugin

    //
    // MODULE: Download ENA metadata
    //
    ENA_METADATA(
        params.study_accession
    )
    ch_versions = ch_versions.mix(ENA_METADATA.out.versions)

    //
    // Split filtered metadata into individual download tasks
    //
    ENA_METADATA.out.metadata
        .splitCsv(header: true, sep: '\t')
        .filter { row ->
            // Apply library strategy filter if provided
            if (params.library_strategy_filter) {
                def library_strategy = row.library_strategy?.toLowerCase()
                def filter_library_strategy = params.library_strategy_filter.toLowerCase()
                if (library_strategy == filter_library_strategy) {
                    log.info("Skipping sample ${row.run_accession} because library_source is ${row.library_strategy}")
                    return false
                }
            }
            // Skip if no FASTQ URLs
            def fastq_urls = row.fastq_ftp
            if (!fastq_urls || fastq_urls.trim().isEmpty()) {
                log.info("No FASTQ URLs found for ${row.run_accession}, skipping")
                return false
            }
            return true
        }
        .map { row ->
            def fastq_urls = row.fastq_ftp?.split(';')?.collect { it.trim() }?.findAll { it }
            def fastq1 = fastq_urls && fastq_urls.size() >= 1 ? "ftp://${fastq_urls[0]}" : null
            def fastq2 = fastq_urls && fastq_urls.size() >= 2 ? "ftp://${fastq_urls[1]}" : null

            def meta = [
                study_accession: params.study_accession,
                run_accession: row.run_accession,
            ]

            [meta, fastq1, fastq2]
        }
        .filter { it[1] != null }
        .set { ch_files_to_download }

    //
    // MODULE: Download FASTQ files
    //
    DOWNLOAD_FASTQ(
        ch_files_to_download
    )
    ch_versions = ch_versions.mix(DOWNLOAD_FASTQ.out.versions.first())

    //
    // MODULE: Create samplesheet based on format
    //
    ch_samplesheet = Channel.empty()

    if (params.samplesheet_format == 'miassembler') {
        CREATE_MIASSEMBLER_SAMPLESHEET(
            ENA_METADATA.out.metadata,
            params.study_accession,
            params.assembler,
            params.memory,
            params.contaminant_reference,
            params.outdir,
            params.library_strategy_filter,
        )
        ch_versions = ch_versions.mix(CREATE_MIASSEMBLER_SAMPLESHEET.out.versions)
        ch_samplesheet = CREATE_MIASSEMBLER_SAMPLESHEET.out.samplesheet
    }

    //
    // Collate and save software versions
    //
    softwareVersionsToYAML(ch_versions)
        .collectFile(
            storeDir: "${params.outdir}/pipeline_info",
            name: 'datagrabber_software_' + 'versions.yml',
            sort: true,
            newLine: true,
        )
        .set { ch_collated_versions }

    emit:
    fastq_files = DOWNLOAD_FASTQ.out.fastq_files // channel: [ meta, [fastq_files] ]
    samplesheet = ch_samplesheet // channel: [ path(samplesheet.csv) ]
    versions    = ch_versions // channel: [ path(versions.yml) ]
}
