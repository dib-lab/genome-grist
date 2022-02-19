"""
TODO:
* allow just gather, as well as allowing mapping+taxonomy.
"""
import pandas as pd

class GristDataFrames:
    def __init__(self, name, all_df, left_df, gather_df, names_df, debug=False):
        self.name = name
        self.all_df = all_df
        self.left_df = left_df
        self.gather_df = gather_df
        self.names_df = names_df
        
        self.debug = debug
        
        self._check()
        
    def _check(self):
        all_df = self.all_df
        left_df = self.left_df
        gather_df = self.gather_df
        names_df = self.names_df

        # this ensures that only rows that share genome_id are in all the dataframes
        in_gather = set(gather_df.genome_id)
        if self.debug:
            print(f'{len(in_gather)} in gather results')
        in_left = set(left_df.genome_id)
        if self.debug:
            print(f'{len(in_left)} in leftover results')

        in_both = in_left.intersection(in_gather)
        if self.debug:
            print(f'{len(in_both)} in both')
            print('diff gather example:', list(in_gather - in_both)[:5])
            print('diff left example:', list(in_left - in_both)[:5])

        assert not in_gather - in_both
        assert not in_left - in_both

        #all_df = all_df[all_df.genome_id.isin(in_both)]
        #left_df = left_df[left_df.genome_id.isin(in_both)]
        #gather_df = gather_df[gather_df.genome_id.isin(in_both)]
        #names_df = names_df[names_df.genome_id.isin(in_both)]

        # reassign index now that we've maybe dropped rows
        #all_df.index = range(len(all_df))
        #left_df.index = range(len(left_df))
        #gather_df.index = range(len(gather_df))
        #names_df.index = range(len(names_df))

        assert len(all_df) == len(gather_df)
        assert len(left_df) == len(gather_df)
        assert len(names_df) == len(gather_df)
        assert len(names_df) == len(in_both)
        
    def subsample_top_n(self, subsample_to):
        left_df = self.left_df[:subsample_to]
        all_df = self.all_df[:subsample_to]
        gather_df = self.gather_df[:subsample_to]
        names_df = self.names_df[:subsample_to]
        
        return self.__class__(self.name, all_df, left_df, gather_df, names_df)

    @classmethod
    def load_sample_dfs(cls, name, sample_id, outdir, debug=False):
        print(f'loading sample {sample_id}')

        # load mapping CSVs
        print(f'reading full mapping results from ../../{outdir}/mapping/{sample_id}.summary.csv')
        all_df = pd.read_csv(f'../../{outdir}/mapping/{sample_id}.summary.csv')
        print(f'reading leftover mapping results from ../../{outdir}/leftover/{sample_id}.summary.csv')
        left_df = pd.read_csv(f'../../{outdir}/leftover/{sample_id}.summary.csv')

        # load gather CSV
        print(f'reading gather results from ../../{outdir}/gather/{sample_id}.gather.csv')
        gather_df = pd.read_csv(f'../../{outdir}/gather/{sample_id}.gather.csv')

        # names!
        print(f'reading genome names from ../../{outdir}/gather/{sample_id}.genomes.info.csv')
        names_df = pd.read_csv(f'../../{outdir}/gather/{sample_id}.genomes.info.csv')

        # connect gather_df to all_df and left_df using 'genome_id'
        def fix_name(x):
            # pick off first whitespace-delimited name as identifier
            x = x.split()[0]

            # eliminate stuff after the period, too.
            x = x.split('.')[0]

            return x

        gather_df['genome_id'] = gather_df['name'].apply(fix_name)
        names_df['genome_id'] = names_df['ident'].apply(fix_name)

        # truncate names at 30 bp:
        TRUNCATE_NAMES_LEN=30
        names_df['orig_display_name'] = names_df['display_name']
        truncate_display_name = lambda x: x[:TRUNCATE_NAMES_LEN] + '...' if len(x) > TRUNCATE_NAMES_LEN else x
        names_df['display_name'] = names_df['orig_display_name'].apply(truncate_display_name)

        # re-sort left_df and all_df to match gather_df order, using matching genome_id column
        all_df = all_df.set_index("genome_id")
        all_df = all_df.reindex(index=gather_df["genome_id"])
        all_df = all_df.reset_index()

        left_df = left_df.set_index("genome_id")
        left_df = left_df.reindex(index=gather_df["genome_id"])
        left_df = left_df.reset_index()

        names_df = names_df.set_index("genome_id")
        names_df = names_df.reindex(index=gather_df["genome_id"])
        names_df = names_df.reset_index()

        sample_df = cls(name, all_df, left_df, gather_df, names_df)
        return sample_df
