#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pyPhyTrees: Phylogenetic Tree Construction and Visualization Tool
Calls external tools (MAFFT and IQ-TREE) using Python's subprocess
and visualizes them in circular format using pycirclize.

This is the main entry point of the application.

For more information, see the README.md file.
"""
import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
import pandas as pd
from omegaconf import OmegaConf
from hydra import initialize, compose

from utils.print_logo import config2logo as show_logo
from utils.help_function import show_help_with_rich
from utils.log import logger_generator


def load_groupings_from_csv(csv_file):
    """
    Load groupings from a CSV file.
    The CSV should have 'sequence' and 'group' columns, and optionally a 'color' column
    """
    df = pd.read_csv(csv_file)
    
    # Check if required columns exist
    if 'sequence' not in df.columns or 'group' not in df.columns:
        raise ValueError("CSV file must contain 'sequence' and 'group' columns")
    
    # Create a dictionary mapping groups to sequences and colors
    groupings = {}
    group_colors = {}
    
    for _, row in df.iterrows():
        seq_name = str(row['sequence']).strip()
        group_name = str(row['group']).strip()
        
        # Add sequence to group
        if group_name not in groupings:
            groupings[group_name] = []
        groupings[group_name].append(seq_name)
        
        # If color is provided, store it
        if 'color' in df.columns:
            color_value = str(row['color']).strip()
            group_colors[group_name] = color_value
    
    return groupings, group_colors


def main():
    """
    Main function that serves as the entry point for the application.
    Uses argparse with subcommands for command-line interface while loading configuration through Hydra.
    """
    # First, load the default config using Hydra
    with initialize(config_path="config", version_base=None):
        cfg = compose(config_name="config")

    # Create the main argument parser with subcommands
    parser = argparse.ArgumentParser(
        description="Build and visualize phylogenetic trees from sequence data using MAFFT and IQ-TREE (subprocess version)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s build sequences.fasta
  %(prog)s build sequences.fasta -o my_tree.png --seq-type dna -B 1000 --threads 4
  %(prog)s build sequences.fasta -g 'Group1:seq1,seq2' -g 'Group2:seq3,seq4'
  %(prog)s plot tree.nwk -o my_tree.png
  %(prog)s plot tree.nwk --relation groups.csv

For detailed help: %(prog)s --help-rich
        '''
    )
    parser.add_argument("--help-rich", action="store_true", help="Show rich formatted help with detailed information")
    parser.add_argument("--show-logo", action="store_true", help="Show rich formatted logo")
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build subcommand
    build_parser = subparsers.add_parser('build', help="Build phylogenetic tree from sequences")
    build_parser.add_argument("input_file", help="Input FASTA file containing sequences")
    build_parser.add_argument("-o", "--output", default="phylogenetic_tree_circular.png", help="Output image file name (default: phylogenetic_tree_circular.png)")
    build_parser.add_argument("--tree-file", default="tree.nwk", help="Output tree file in Newick format (default: tree.nwk)")
    build_parser.add_argument("--alignment-file", default="aligned.fasta", help="Output alignment file in FASTA format (default: aligned.fasta)")
    build_parser.add_argument("--seq-type", choices=['dna', 'rna', 'protein'], help="Sequence type (auto-detected if not provided)")
    build_parser.add_argument("-B", "--bootstrap", type=int, default=100, help="Number of Ultrafast Bootstrap replicates for IQ-TREE (default: 100, minimum: 1000)")
    build_parser.add_argument("--threads", type=int, default=1, help="Number of threads to use for MAFFT and IQ-TREE (default: 1)")
    build_parser.add_argument("-g", "--group", action="append", metavar="GROUP:SPECIES", help="Group species for visualization (format: GroupName:Species1,Species2,...). Can be used multiple times.")
    build_parser.add_argument("--relation", help="CSV file containing sequence to group relations (format: 'sequence,group' columns)")
    build_parser.add_argument("--visualization-style", choices=['circular', 'rectangular', 'radial', 'heatmap', 'all'],
                              default='circular', help="Type of visualization to generate (default: circular)")
    build_parser.add_argument("--keep-all-files", action="store_true", help="Keep all intermediate files (alignment, logs, etc.)")
    
    # Plot subcommand
    plot_parser = subparsers.add_parser('plot', help="Plot phylogenetic tree from existing tree file")
    plot_parser.add_argument("tree_file", help="Input tree file in Newick format")
    plot_parser.add_argument("-o", "--output", default="phylogenetic_tree_circular.png", help="Output image file name (default: phylogenetic_tree_circular.png)")
    plot_parser.add_argument("-g", "--group", action="append", metavar="GROUP:SPECIES", help="Group species for visualization (format: GroupName:Species1,Species2,...). Can be used multiple times.")
    plot_parser.add_argument("--relation", help="CSV file containing sequence to group relations (format: 'sequence,group' columns)")
    plot_parser.add_argument("--visualization-style", choices=['circular', 'rectangular', 'radial', 'heatmap', 'all'],
                              default='circular', help="Type of visualization to generate (default: circular)")

    args = parser.parse_args()

    # Handle special flags first
    if args.help_rich:
        show_logo(cfg)
        show_help_with_rich(cfg)
        return
    elif args.show_logo:
        show_logo(cfg)
        return
    elif not args.command:
        # Show logo and help if no command is provided
        show_logo(cfg)
        show_help_with_rich(cfg)
        return

    # Show the rich logo during normal execution
    show_logo(cfg)

    # Import visualization functions
    from scripts.Visualize import visualize_tree_circular, visualize_tree_rectangular, visualize_tree_radial, visualize_tree_with_heatmap, visualize_all_styles

    if args.command == "build":
        # Set default values for config
        cfg.output = args.output or cfg.get('output', 'phylogenetic_tree_circular.png')
        cfg.tree_file = args.tree_file or cfg.get('tree_file', 'tree.nwk')
        cfg.alignment_file = args.alignment_file or cfg.get('alignment_file', 'aligned.fasta')
        cfg.seq_type = args.seq_type
        cfg.bootstrap = args.bootstrap if args.bootstrap is not None else cfg.get('bootstrap', 100)
        cfg.threads = args.threads or cfg.get('threads', 1)
        cfg.group = args.group or cfg.get('group', None)
        cfg.keep_all_files = args.keep_all_files or cfg.get('keep_all_files', False)

        # Set input file in the config
        cfg.input_file = args.input_file

        # Import and run the core functionality
        from scripts.PhyTrees import core_function
        core_function(cfg, args)
    elif args.command == "plot":
        # Handle groupings for plotting
        groupings = {}
        group_colors = {}
        
        # Load groupings from CSV if provided
        if args.relation:
            try:
                groupings, group_colors = load_groupings_from_csv(args.relation)
            except Exception as e:
                print(f"Error loading groupings from CSV: {e}")
                sys.exit(1)
        
        # Also handle traditional -g format if provided
        if args.group:
            for group_spec in args.group:
                try:
                    group_name, species_list = group_spec.split(":", 1)
                    species = [s.strip() for s in species_list.split(",")]
                    if group_name in groupings:
                        # Merge with existing group
                        groupings[group_name].extend(species)
                    else:
                        groupings[group_name] = species
                    # If group_colors are not provided, generate random colors
                    if not group_colors and group_name not in group_colors:
                        import matplotlib.colors as mcolors
                        # Generate a random color
                        group_colors[group_name] = mcolors.to_hex(mcolors.hsv_to_rgb([len(group_colors) / 10.0, 0.8, 0.8]))
                except ValueError:
                    print(f"Invalid group format: {group_spec}. Use GroupName:Species1,Species2,...")
                    sys.exit(1)

        # Determine visualization style and call the appropriate function
        logger, _ = logger_generator(cfg)
        viz_success = False
        
        if args.visualization_style == 'circular':
            viz_success = visualize_tree_circular(args.tree_file, args.output, groupings, group_colors, logger)
        elif args.visualization_style == 'rectangular':
            viz_success = visualize_tree_rectangular(args.tree_file, args.output, groupings, group_colors, logger)
        elif args.visualization_style == 'radial':
            viz_success = visualize_tree_radial(args.tree_file, args.output, groupings, group_colors, logger)
        elif args.visualization_style == 'heatmap':
            viz_success = visualize_tree_with_heatmap(args.tree_file, args.output, groupings, group_colors, logger)
        elif args.visualization_style == 'all':
            output_prefix = args.output.replace('.png', '').replace('.pdf', '')
            viz_success = visualize_all_styles(args.tree_file, output_prefix, groupings, group_colors, logger)
        
        if not viz_success:
            logger.error("Visualization failed")
            sys.exit(1)
        else:
            logger.info("Plotting completed successfully!")


if __name__ == "__main__":
    main()