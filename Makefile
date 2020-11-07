test:
	genome-grist process HSMA33MX smash_reads
	cp tests/test-data/HSMA33MX.x.genbank.gather.csv outputs/genbank/
	touch outputs/genbank/HSMA33MX.x.genbank.gather.out
	genome-grist process HSMA33MX summarize -j 8
