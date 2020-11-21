all: clean-test test

clean-test:
	rm -fr outputs.test.HSMA33MX/

test:
	genome-grist run tests/test-data/HSMA33MX.conf trim_reads -j 8 -p
	# have to run this w/o conda to take advantage of latest sourmash @CTB
	genome-grist run tests/test-data/HSMA33MX.conf gather_genbank -j 8 -p --no-use-conda
	genome-grist run tests/test-data/HSMA33MX.conf summarize -j 8 -p
	genome-grist run tests/test-data/HSMA33MX.conf build_consensus -j 8 -p
	genome-grist run tests/test-data/HSMA33MX.conf make_sgc_conf -p

flakes:
	flake8 --ignore=E501 genome_grist/ tests/

black:
	black .

