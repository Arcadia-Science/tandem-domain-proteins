# 2026-tandem-domain-proteins

[![run with conda](https://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/projects/miniconda/en/latest/)

This repo contains the data and code associated with the pub: [Assembly and annotation artifacts can lead to problematic protein structural inferences](https://doi.org/10.57844/arcadia-2u60-81sg).

## Purpose

Protein structure prediction algorithms appear to output tandem-dimers and tandem-trimers of otherwise monomeric proteins. Here we investigate the composition of tandem-domain proteins across <i>Drosophila</i> species and show that they appear to comprise multiple different proteins. This work has implications for the widespread use of inferred protein structures.

## Installation and Setup

To run the analyses in this workflow first clone the github repo using

```{bash}
git clone https://github.com/Arcadia-Science/2026-tandem-domain-proteins
```

This repository uses conda to manage software environments and installations. You can find operating system-specific instructions for installing miniconda [here](https://docs.conda.io/projects/miniconda/en/latest/). After installing conda and [mamba](https://mamba.readthedocs.io/en/latest/), run the following command to create the pipeline run environment.

```{bash}
mamba env create -n tandem-domain-proteins --file envs/environment.yml
conda activate tandem-domain-proteins
```

Once the environment is loaded you can run the full analysis by opening and running `full_HMMsplit_analyze_pipeline.ipynb`

## Data

The `tips_data/` folder contains all input files required to run the pipeline including:  
- `select.fasta` - a FASTA file containing the 73 <i>Drosophila</i> protein sequences downloaded from the TIPS database  
- `Q9VB3_B4KE22.fasta` - an additional FASTA file containing the 2 protein sequences of the reference proteins Q9VB3 and B4KE33  
- `AF-B4KE22-F1-model_v6.pdb` - protein .pdb file for the reference protein B4KE22  
- `AF-Q9VBV3-F1-model_v6.pdb` - protein .pdb file for the reference protein Q9VBV3  
- `mmseq2out.xlsx` - output metadata from our TIPS database query  
- and the folder `Structure/` which contains the .pdb protein structures from the TIPS database  

## Overview

### Description of the folder structure

All other folders are output by the pipeline and include:
- `repeat_detection_results/` - results from coarse binning of monomers for training profile HMM
- `blast_db/` - <i>D. melanogaster</i> blast database
- `blastp_output/` - BLASTp search results from various representative proteins
- `output_files/` - all output files including pairwise patristic distances, sequence divergence, and TM-scores
- `output_plots/` - all plots outputted by pipeline
- `pdb_domains/` - all split domain pdbs
- `protein_visualizer/` - contains the models and code to generate the protein visualizer embedded in the pub

### Compute Specifications

This analysis was run on macOS Sequoia 15.5, with 12 cores and 24Gb RAM.

## Contributing

See how we recognize [feedback and contributions to our code](https://github.com/Arcadia-Science/arcadia-software-handbook/blob/main/guides-and-standards/guide--credit-for-contributions.md).

---
## For Developers

This section contains information for developers who are working off of this template. Please adjust or edit this section as appropriate when you're ready to share your repo.

### GitHub templates
This template uses GitHub templates to provide checklists when making new pull requests. These templates are stored in the [.github/](./.github/) directory.

### VSCode
This template includes recommendations to VSCode users for extensions, particularly the `ruff` linter. These recommendations are stored in `.vscode/extensions.json`. When you open the repository in VSCode, you should see a prompt to install the recommended extensions.

### `.gitignore`
This template uses a `.gitignore` file to prevent certain files from being committed to the repository.

### `pyproject.toml`
`pyproject.toml` is a configuration file to specify your project's metadata and to set the behavior of other tools such as linters, type checkers etc. You can learn more [here](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

### Linting
This template automates linting and formatting using GitHub Actions and the `ruff` linter. When you push changes to your repository, GitHub will automatically run the linter and report any errors, blocking merges until they are resolved.
