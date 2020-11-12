#!/bin/bash -login
#SBATCH -p med2                # partition, or queue, to assign to
#SBATCH -J gather-paper            # name for job
#SBATCH -N 1                   # one "node", or computer
#SBATCH -n 1                   # one task for this node
#SBATCH -c 16                  # cores per task
#SBATCH -t 2-0                 # ask for 2 days
#SBATCH --mem=80000             # memory (30,000 mb = 30gb)
#SBATCH --mail-type=ALL
#SBATCH --mail-user=titus@idyll.org

# initialize conda
. ~/miniconda3/etc/profile.d/conda.sh

# activate your desired conda environment
conda activate charcoal

# fail on weird errors
set -o nounset
set -o errexit
set -x

# go to the directory you ran 'sbatch' in, OR just hardcode it...
#cd $SLURM_SUBMIT_DIR
cd ~/genome-grist

# run the snakemake!
genome-grist process SRR4027592 gather_genbank summarize -j 16

# print out various information about the job
env | grep SLURM            # Print out values of the current jobs SLURM environment variables

scontrol show job ${SLURM_JOB_ID}     # Print out final statistics about resource uses before job exits

sstat --format 'JobID,MaxRSS,AveCPU' -P ${SLURM_JOB_ID}.batch
