test:
	genome-grist run tests/test-data/HSMA33MX.conf summarize -j 8 -p --no-use-conda
	genome-grist run tests/test-data/HSMA33MX.conf smash_reads -j 8 -p --no-use-conda

flakes:
	flake8 --ignore=E501 genome_grist/ tests/

black:
	black .

