[中文文档](./docs/README-cn.md) | English
# pyPhyTrees

A Python script for phylogenetic tree construction and visualization using MAFFT and IQ-TREE.

## Overview

This script automates the process of phylogenetic tree construction by:
- Aligning sequences using MAFFT
- Building phylogenetic trees with IQ-TREE
- Creating various visualizations including circular, rectangular, radial, and heatmap layouts

### New Features
- **Custom Color Support**: Use a CSV file to specify custom colors for groups with the `--relation` parameter
- **Multiple Visualization Styles**: Support for circular, rectangular, radial, and heatmap visualizations
- **Distance-based Coloring**: Default coloring based on evolutionary distances (can be overridden with grouping)
- **CSV-based Grouping**: Support for sequence group specifications via CSV files with format: `sequence,group,color` (color optional)

## Dependencies

### Required Software

The script requires the following external tools to be installed and available in your PATH:

1. **MAFFT** v7.525 or higher
   - Version tested: v7.526 (2024/Apr/26)
   - Multiple sequence alignment tool
   - Homepage: https://mafft.cbrc.jp/alignment/software/

2. **IQ-TREE** v3.0.1 or higher
   - Version tested: v3.0.1 (2025/May/5)
   - Phylogenetic tree inference software
   - Homepage: http://www.iqtree.org

### Python Dependencies

The script requires the following Python packages:

- Biopython
- pycirclize
- matplotlib
- pandas
- rich
- hydra-core
- omegaconf

## Installation

### Installing External Dependencies

#### Using Conda
```bash
conda install -c bioconda mafft iqtree
```

#### Manual Installation
- Download MAFFT from: https://mafft.cbrc.jp/alignment/software/
- Download IQ-TREE from: http://www.iqtree.org

### Installing Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python main.py sequences.fasta
```

### Custom Output and Parameters
```bash
python main.py sequences.fasta -o my_tree.png --seq-type dna -B 1000
```

### Grouping Visualization with Traditional Format
```bash
python main.py sequences.fasta -g 'Group1:seq1,seq2' -g 'Group2:seq3,seq4'
```

### Group Visualization with CSV File (New Feature)
Create a CSV file with format: `sequence,group,color` (color is optional)
```csv
sequence,group,color
seq1,GroupA,#FF0000
seq2,GroupA,#FF0000
seq3,GroupB,#0000FF
seq4,GroupB,#0000FF
```

Then use:
```bash
python main.py sequences.fasta --relation groups.csv
```

### Multiple Visualization Styles
```bash
# Circular visualization (default)
python main.py sequences.fasta --visualization-style circular

# Rectangular visualization
python main.py sequences.fasta --visualization-style rectangular

# Radial visualization
python main.py sequences.fasta --visualization-style radial

# Heatmap visualization
python main.py sequences.fasta --visualization-style heatmap

# All styles
python main.py sequences.fasta --visualization-style all
```

### Rich Help
```bash
python main.py --help-rich
```

### Show Logo
```bash
python main.py --show-logo
```

## Command Line Options

### Build Command (for creating trees from sequences)
| Option | Description | Default |
|--------|-------------|---------|
| `INPUT_FILE` | Input FASTA file containing sequences | |
| `-o, --output` | Output image file name | `phylogenetic_tree_circular.png` |
| `--tree-file` | Output tree file in Newick format | `tree.nwk` |
| `--alignment-file` | Output alignment file in FASTA format | `aligned.fasta` |
| `--seq-type` | Sequence type (auto-detected if not provided) | `auto` |
| `-B, --bootstrap` | Number of Ultrafast Bootstrap replicates for IQ-TREE (minimum 1000) | `100` (will be adjusted to 1000 minimum) |
| `--threads` | Number of threads to use for MAFFT and IQ-TREE | `1` |
| `-g, --group` | Group species for visualization (format: GroupName:Species1,Species2,...). Can be used multiple times. | |
| `--relation` | CSV file containing sequence to group relations (format: 'sequence,group' columns) | |
| `--visualization-style` | Type of visualization to generate (circular, rectangular, radial, heatmap, all) | `circular` |
| `--keep-all-files` | Keep all intermediate files (alignment, logs, etc.) | `False` |

### Plot Command (for visualizing existing trees)
| Option | Description | Default |
|--------|-------------|---------|
| `TREE_FILE` | Input tree file in Newick format | |
| `-o, --output` | Output image file name | `phylogenetic_tree_circular.png` |
| `-g, --group` | Group species for visualization (format: GroupName:Species1,Species2,...). Can be used multiple times. | |
| `--relation` | CSV file containing sequence to group relations (format: 'sequence,group' columns) | |
| `--visualization-style` | Type of visualization to generate (circular, rectangular, radial, heatmap, all) | `circular` |

## CSV Format for Group Relations

The `--relation` option accepts CSV files with the following columns:
- `sequence`: The name of the sequence as it appears in the FASTA/phylogenetic tree
- `group`: The group name for this sequence
- `color` (optional): The hex color code for this group (e.g., #FF0000, red)

Example CSV file:
```csv
sequence,group,color
gene00975,GroupA,#FF0000
gene01152,GroupA,#FF0000
gene03450,GroupA,#FF0000
gene01844,GroupB,#0000FF
gene04400,GroupB,#0000FF
gene01985,GroupC,#00FF00
gene08479,GroupC,#00FF00
```

You can also use a simpler format without colors, and the system will automatically assign colors:
```csv
sequence,group
seq1,GroupA
seq2,GroupA
seq3,GroupB
seq4,GroupB
```

## Features

- **Automatic Sequence Type Detection**: Automatically detects if sequences are DNA, RNA, or protein
- **Rich Formatted Output**: Beautifully styled command-line interface with logo and help
- **Multiple Visualization Styles**: Creates publication-ready visualizations in various formats
- **Group Visualization**: Color-code different groups of species in the visualization with custom colors
- **Distance-based Coloring**: Default coloring based on evolutionary distances
- **Automatic File Cleanup**: Removes intermediate files after completion (unless `--keep-all-files` is specified)
- **Flexible Grouping**: Support for both traditional `-g` flag and CSV-based grouping
- **Legend Support**: All visualizations include legends showing group-color mappings

## Input Requirements

- Input file must be in FASTA format for building trees
- For plotting existing trees, use Newick format (.nwk)
- At least 3 sequences are required for phylogenetic analysis
- CSV files for grouping must contain 'sequence' and 'group' columns

## Output

- Various visualization of the phylogenetic tree (depending on selected style)
- Newick tree file (default: `tree.nwk`)
- Optionally, alignment file and IQ-TREE output files
- All visualizations include legends when grouping is used

## Troubleshooting

### Common Issues

1. **Command not found**:
   - Ensure MAFFT and IQ-TREE are installed and in your PATH
   - Use `mafft -v` and `iqtree3 -v` to verify installation

2. **IQ-TREE bootstrap requirement**:
   - The script automatically adjusts bootstrap values to minimum 1000 required by IQ-TREE

3. **Visualization libraries missing**:
   - Install with: `pip install -r requirements.txt`

4. **CSV file format error**:
   - Ensure required columns 'sequence' and 'group' exist in your CSV file
   - Check that sequence names match those in your FASTA/phylogenetic tree

5. **Color format error**:
   - When using custom colors, ensure they are in valid hex format (e.g., #FF0000)

## Examples

### Basic Tree Building and Visualization
```bash
python main.py sequences.fasta -o my_tree.png
```

### Building with Custom Groups
```bash
python main.py sequences.fasta --relation groups.csv --visualization-style all
```

### Visualizing Existing Tree with Custom Groups
```bash
python main.py plot tree.nwk --relation groups.csv --visualization-style rectangular
```

## License

This project is open-source. See the LICENSE file for details.