all: clean-test test

flakes:
	flake8 --ignore=E501 genome_grist/ tests/

black:
	black .

clean-test:
	rm -fr outputs.test/

clean-gather:
	genome-grist run tests/test-data/SRR5950647.conf clean_gather

test:
	genome-grist run tests/test-data/SRR5950647.conf summarize_mapping summarize_tax make_sgc_conf -j 8 -p -k

	# try various targets to make sure they work
	genome-grist run tests/test-data/SRR5950647.conf download_genbank_genomes \
	    combine_genome_info retrieve_genomes estimate_distinct_kmers \
	    count_trimmed_reads summarize_sample_info abundtrim_reads -j 8 -p

### private/local genomes test stuff

test-private: outputs.private/trim/podar.trim.fq.gz \
		databases/podar-ref.zip  databases/podar-ref.info.csv \
		databases/podar-ref.tax.csv
	genome-grist run conf-private.yml summarize_gather summarize_mapping summarize_tax -j 4 -p

# download the (subsampled) reads for SRR606249
outputs.private/trim/podar.trim.fq.gz:
	mkdir -p outputs.private/trim
	curl -L https://osf.io/ckbq3/download -o outputs.private/trim/podar.trim.fq.gz

# download the ref genomes
databases/podar-ref/: 
	mkdir -p databases/podar-ref
	curl -L https://osf.io/vbhy5/download -o databases/podar-ref.tar.gz
	cd databases/podar-ref/ && tar xzf ../podar-ref.tar.gz
	parallel -j 4 gzip {} ::: $$(ls databases/podar-ref/*.fa)

# sketch the ref genomes
databases/podar-ref.zip: databases/podar-ref/
	sourmash sketch dna -p k=31,scaled=1000 --name-from-first \
	    databases/podar-ref/*.fa.gz -o databases/podar-ref.zip

# download taxonomy
databases/podar-ref.tax.csv:
	curl -L https://osf.io/4yhjw/download -o databases/podar-ref.tax.csv

# create info file and genomes directory:
databases/podar-ref.info.csv:
	python -m genome_grist.copy_local_genomes databases/podar-ref/*.fa.gz -o databases/podar-ref.info.csv -d databases/podar-ref.d
	python -m genome_grist.make_info_file databases/podar-ref.info.csv
