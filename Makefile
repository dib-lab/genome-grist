all: clean-test test

clean-test:
	rm -fr outputs.test.HSMA33MX/

test:
	genome-grist run tests/test-data/HSMA33MX.conf summarize make_sgc_conf -j 8 -p
	genome-grist run tests/test-data/HSMA33MX.conf summarize make_sgc_conf -j 8 -p

flakes:
	flake8 --ignore=E501 genome_grist/ tests/

black:
	black .

