import math
from pickle import TRUE
from random import sample
import pandas as pd
import glob
from collections import defaultdict
from sourmash.lca import lca_utils
from sourmash.lca.lca_utils import LineagePair
import sys
import os
import plotly.graph_objects as go

if len(sys.argv < 3):
    print("usage: python report-taxonomy.py <sample_id>.gather.with-lineages.csv <output_path>", file=sys.stderr)
    sys.exit(-1)

# Parameters
render = ""
gather_csv = sys.argv[1]
output_html = sys.argv[2]
sample_id = os.path.basename(gather_csv).replace(
    '.gather.with-lineages.csv', '')
tax_df = pd.read_csv(gather_csv)
tax_ranks = ['superkingdom', 'phylum', 'class',
             'order', 'family', 'genus', 'species']

# "fix" lineage column,


def split_lineages(x):
    #    print((x, type(x)))
    if isinstance(x, float) and math.isnan(x):
        return ()

    ret = []
    for (rank, name) in zip(tax_ranks, x.split(';')):
        ret.append(LineagePair(rank, name))
    return tuple(ret)


tax_df['lineage'] = tax_df['lineage'].apply(split_lineages)

# and break it up into tuples


def grab_tax(x, idx):
    if x:
        return x[idx].name
    return ''


for idx, rank in enumerate(tax_ranks):
    tax_df[rank] = tax_df['lineage'].apply(grab_tax, args=(idx,))


# create function that aggregates various pieces of information by rank & builds a new df
def aggregate_by_rank(df, rank):
    # first, build all the counts
    unique_intersect_by_rank = defaultdict(int)
    f_intersect_by_rank = defaultdict(int)
    best_hashes_by_rank = {}

    def sum_unique(row):
        lin = row.lineage
        if pd.isnull(lin):
            lin = []
        unique_hashes = row.unique_intersect_bp
        f_hashes = row.f_unique_to_query

        for rank in ('superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species'):
            poplin = lca_utils.pop_to_rank(lin, rank)
            unique_intersect_by_rank[poplin] += unique_hashes
            f_intersect_by_rank[poplin] += f_hashes

            best_hashes = best_hashes_by_rank.get(poplin, 0)
            if best_hashes < unique_hashes:
                best_hashes_by_rank[poplin] = unique_hashes

    df.apply(sum_unique, axis=1)

    # now do the sorting etc.
    rank_counts = []
    for lin, bp in sorted(unique_intersect_by_rank.items(), key=lambda x: -x[1]):
        if lin and lin[-1].rank == rank:

            f_unique = f_intersect_by_rank[lin]
            if rank == 'species':
                name = lin[-1].name
                name = f'{name} ({lin[0].name})'
            elif rank == 'genus':
                name = lin[-1].name
                name = f'{name}'
            else:
                name = lca_utils.display_lineage(lin)

            rank_counts.append(dict(name=name, hashes=bp, f_unique=f_unique,
                                    best_hashes=best_hashes_by_rank[lin],
                                    lineage=lin))

    return pd.DataFrame(rank_counts)


"""
ALL RANKS DFs
"""

rank_to_df = {}
for rank in tax_ranks[:0:-1]:
    rank_to_df[rank] = aggregate_by_rank(tax_df, rank)
    rank_to_df[rank]['f_unique'] = rank_to_df[rank]['f_unique'].apply(
        lambda x: x*100)

rank_to_fig = {}

for rank in tax_ranks[:0:-1]:
    fig = go.Figure(data=go.Scatter(
        mode='markers',
        marker=dict(color='LightSkyBlue', size=5,
                    line=dict(color='MediumPurple', width=1)),
        x=rank_to_df[rank]['f_unique'],
        y=rank_to_df[rank]['name']),
        layout=go.Layout(
            # variable height based on data size
            height=max(len(rank_to_df[rank]) * 18, 100),
            barmode='stack',
            yaxis={'categoryorder': 'total ascending'},
            title={
                'text': f"{sample_id}: metagenome classification, by {rank}",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title="Percent of metagenome"
            ),
    )
    )
    rank_to_fig[rank] = fig


with open(output_html, 'w') as f:
    for rank, fig in rank_to_fig.items():
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
