all: clean-test test

clean-test:
	rm -fr outputs.test/

test:
	genome-grist run tests/test-data/SRR5950647.conf summarize_mapping summarize_tax make_sgc_conf -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf summarize_mapping summarize_tax make_sgc_conf -j 8 -p

	# try various targets to make sure they work
	genome-grist run tests/test-data/SRR5950647.conf download_matching_genomes -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf download_matching_genomes_info -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf estimate_distinct_kmers -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf count_trimmed_reads -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf summarize_sample_info -j 8 -p


flakes:
	flake8 --ignore=E501 genome_grist/ tests/

black:
	black .
