all: clean-test test

clean-test:
	rm -fr outputs.test/

test:
	genome-grist run tests/test-data/SRR5950647.conf summarize make_sgc_conf -j 8 -p
	genome-grist run tests/test-data/SRR5950647.conf summarize make_sgc_conf -j 8 -p

flakes:
	flake8 --ignore=E501 genome_grist/ tests/

black:
	black .

