#!/bin/bash -login
#SBATCH -p bmm                # partition, or queue, to assign to
#SBATCH -J gather-paper            # name for job
#SBATCH -N 1                   # one "node", or computer
#SBATCH -n 1                   # one task for this node
#SBATCH -c 32                  # cores per task
#SBATCH -t 5-0                 # ask for 2 days
#SBATCH --mem=120000             # memory (30,000 mb = 30gb)
#SBATCH --mail-type=ALL
#SBATCH --mail-user=titus@idyll.org

# initialize conda
. ~/miniconda3/etc/profile.d/conda.sh

# activate your desired conda environment
conda activate grist3

# fail on weird errors
set -o nounset
set -o errexit
set -x

# go to the directory you ran 'sbatch' in, OR just hardcode it...
#cd $SLURM_SUBMIT_DIR
cd ~/genome-grist

# run the snakemake!
genome-grist run conf-paper.yml -k --unlock -j 4
genome-grist run conf-paper.yml -k --resources mem_mb=210000 -j 32 summarize_tax summarize_gather summarize_mapping

# print out various information about the job
env | grep SLURM            # Print out values of the current jobs SLURM environment variables

scontrol show job ${SLURM_JOB_ID}     # Print out final statistics about resource uses before job exits

sstat --format 'JobID,MaxRSS,AveCPU' -P ${SLURM_JOB_ID}.batch
