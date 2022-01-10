all: clean-test test

clean-test:
	rm -fr outputs.test/

test:
	genome-grist run tests/test-data/SRR5950647.conf summarize_mapping summarize_tax make_sgc_conf -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf summarize_mapping summarize_tax make_sgc_conf -j 8 -p

	# try various targets to make sure they work
	genome-grist run tests/test-data/SRR5950647.conf download_genbank_genomes -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf combine_genome_info -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf retrieve_genomes -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf estimate_distinct_kmers -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf count_trimmed_reads -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf summarize_sample_info -j 8 -p

test-private:
	mkdir -p outputs.private/abundtrim
	# download the reads
	curl -L https://osf.io/ckbq3/download -o outputs.private2/abundtrim/podar.abundtrim.fq.gz

	# download the ref genomes
	mkdir -p databases/podar-ref
	curl -L https://osf.io/vbhy5/download -o databases/podar-ref.tar.gz
	cd databases/podar-ref/ && tar xzf ../podar-ref.tar.gz


flakes:
	flake8 --ignore=E501 genome_grist/ tests/

black:
	black .
