test:
	genome-grist run tests/test-data/HSMA33MX.conf summarize -j 8 -p

flakes:
	flake8 genome_grist/ tests/

black:
	black .

