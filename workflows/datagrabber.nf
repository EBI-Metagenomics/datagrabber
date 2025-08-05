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
    ch_run_accessions_include = params.run_accessions_include ? 
        Channel.fromPath(params.run_accessions_include, checkIfExists: true) : 
        file('OPTIONAL_FILE')
    
    ENA_METADATA(
        params.study_accession,
        params.library_strategy_filter,
        ch_run_accessions_include
    )
    ch_versions = ch_versions.mix(ENA_METADATA.out.versions)

    //
    // Split metadata into individual download tasks
    //
    ENA_METADATA.out.metadata
        .splitCsv(header: true, sep: '\t')
        .map { row ->
            def fastq_urls = row.fastq_ftp?.split(';')?.collect { it.trim() }?.findAll { it }
            
            // For PAIRED layout, prefer files with _1 and _2 suffixes
            def fastq1 = null
            def fastq2 = null
            
            if (row.library_layout?.toLowerCase() == 'paired' && fastq_urls?.size() > 2) {
                // Look for _1 and _2 paired files
                def paired1 = fastq_urls.find { it.contains('_1.fastq') }
                def paired2 = fastq_urls.find { it.contains('_2.fastq') }
                
                if (paired1 && paired2) {
                    fastq1 = "ftp://${paired1}"
                    fastq2 = "ftp://${paired2}"
                } else {
                    // Fallback to first two files if _1/_2 pattern not found
                    fastq1 = fastq_urls && fastq_urls.size() >= 1 ? "ftp://${fastq_urls[0]}" : null
                    fastq2 = fastq_urls && fastq_urls.size() >= 2 ? "ftp://${fastq_urls[1]}" : null
                }
            } else {
                // For SINGLE layout or when not enough files, use original logic
                fastq1 = fastq_urls && fastq_urls.size() >= 1 ? "ftp://${fastq_urls[0]}" : null
                fastq2 = fastq_urls && fastq_urls.size() >= 2 ? "ftp://${fastq_urls[1]}" : null
            }

            def meta = [
                study_accession: params.study_accession,
                run_accession: row.run_accession,
                library_layout: row.library_layout,
            ]

            [meta, fastq1, fastq2]
        }
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
