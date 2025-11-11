#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
from Bio import Phylo, SeqIO
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import print
from rich.table import Table
import rich
from omegaconf import DictConfig
from utils.log import logger_generator
from utils.help_function import show_help_with_rich, check_dependencies, read_sequences_from_file, show_logo
from scripts.Visualize import visualize_tree_circular, visualize_tree_rectangular, visualize_tree_radial, visualize_tree_with_heatmap, visualize_all_styles


def run_mafft(input_fasta, output_alignment, threads=1, logger=None):
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)
    
    logger.info(f"Starting MAFFT alignment...")
    cmd = ['mafft', '--thread', str(threads), '--auto', input_fasta]
    logger.info(f"Executing command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        with open(output_alignment, 'w') as f_out:
            f_out.write(result.stdout)
        if result.stderr:
            logger.info(f"MAFFT stderr:\n{result.stderr}")
        logger.info(f"MAFFT alignment completed. Saved to {output_alignment}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"MAFFT failed with return code {e.returncode}")
        logger.error(f"Error output:\n{e.stderr}")
        return False

def run_iqtree(alignment_file, seq_type, bootstrap=1000, threads=1, logger=None):
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)
        
    logger.info(f"Starting IQ-TREE for tree construction...")
    iq_seq_type = 'AA' if seq_type == 'protein' else 'DNA'
    output_prefix = str(Path(alignment_file).with_suffix(''))
    bootstrap = max(bootstrap, 1000) 
    cmd = [
        'iqtree3',
        '-s', alignment_file,
        '-st', iq_seq_type,
        '-m', 'MFP',
        '-B', str(bootstrap),
        '-T', str(threads),
        '-pre', output_prefix
    ]
    logger.info(f"Executing command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        logger.info(f"IQ-TREE output:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"IQ-TREE stderr:\n{result.stderr}")
        tree_file = f"{output_prefix}.treefile"
        if not os.path.exists(tree_file):
            raise FileNotFoundError(f"IQ-TREE finished but output tree file '{tree_file}' was not found.")
        logger.info(f"IQ-TREE construction completed. Tree saved to {tree_file}")
        return tree_file
    except subprocess.CalledProcessError as e:
        logger.error(f"IQ-TREE failed with return code {e.returncode}")
        logger.error(f"Error output:\n{e.stderr}")
        raise

def detect_sequence_type(sequences, logger=None):
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)
        
    protein_chars = set('EFILPQXZJUO*')
    dna_chars = set('ACGT')
    rna_chars = set('ACGU')
    all_chars = set()
    for seq in sequences: all_chars.update(seq.upper())
    if protein_chars & all_chars:
        logger.info("Detected protein sequences")
        return 'protein'
    nucleic_acid_content = (dna_chars | rna_chars | set('N-.X'))
    if all_chars.issubset(nucleic_acid_content):
        if 'U' in all_chars and 'T' not in all_chars:
            logger.info("Detected RNA sequences")
            return 'rna'
        else:
            logger.info("Detected DNA sequences")
            return 'dna'
    logger.info("Could not reliably detect sequence type, defaulting to protein.")
    return 'protein'

def cleanup_files(prefix, extensions, keep_files, logger=None):
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)
        
    logger.info("Cleaning up intermediate files...")
    for ext in extensions:
        file_path = f"{prefix}{ext}"
        if file_path not in keep_files and os.path.exists(file_path):
            try:
                os.unlink(file_path)
                logger.info(f"Removed: {file_path}")
            except OSError as e:
                logger.warning(f"Could not remove {file_path}: {e}")

def core_function(cfg: DictConfig = None, args=None):
    if cfg is None:
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({
            "logs": {"log_level": "INFO", "more_info": True, "project_id": "pyPhyTrees"},
            "software": {
                "version": "v0.1",
                "app_name": "pyPhyTrees",
                "description": "Phylogenetic Tree Construction and Visualization Tool"
            }
        })
    
    logger, output_dir = logger_generator(cfg)
    
    # If args is not provided, create default args
    if args is None:
        import argparse
        parser = argparse.ArgumentParser(
            description="Build and visualize phylogenetic trees from sequence data using MAFFT and IQ-TREE (subprocess version)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=''' 
Examples:
  %(prog)s sequences.fasta
  %(prog)s sequences.fasta -o my_tree.png --seq-type dna -B 1000 --threads 4
  %(prog)s sequences.fasta -g 'Group1:seq1,seq2' -g 'Group2:seq3,seq4'

For detailed help: %(prog)s --help-rich
            '''
        )
        parser.add_argument("input_file", nargs='?', help="Input FASTA file containing sequences")
        parser.add_argument("-o", "--output", default="phylogenetic_tree_circular.png", help="Output image file name (default: phylogenetic_tree_circular.png)")
        parser.add_argument("--tree-file", default="tree.nwk", help="Output tree file in Newick format (default: tree.nwk)")
        parser.add_argument("--alignment-file", default="aligned.fasta", help="Output alignment file in FASTA format (default: aligned.fasta)")
        parser.add_argument("--seq-type", choices=['dna', 'rna', 'protein'], default=None, help="Sequence type (auto-detected if not provided)")
        parser.add_argument("-B", "--bootstrap", type=int, default=100, help="Number of Ultrafast Bootstrap replicates for IQ-TREE (default: 100, minimum: 1000)")
        parser.add_argument("--threads", type=int, default=1, help="Number of threads to use for MAFFT and IQ-TREE (default: 1)")
        parser.add_argument("-g", "--group", action="append", metavar="GROUP:SPECIES", help="Group species for visualization (format: GroupName:Species1,Species2,...). Can be used multiple times.")
        parser.add_argument("--keep-all-files", action="store_true", help="Keep all intermediate files (alignment, logs, etc.)")
        parser.add_argument("--visualization-style", choices=['circular', 'rectangular', 'radial', 'heatmap', 'all'], 
                          default='circular', help="Type of visualization to generate (default: circular)")
        parser.add_argument("--help-rich", action="store_true", help="Show rich formatted help with detailed information")
        parser.add_argument("--show-logo", action="store_true", help="Show rich formatted logo")
        
        args = parser.parse_args()
    
    groupings = {}
    if args.group:
        for group_spec in args.group:
            try:
                group_name, species_list = group_spec.split(":", 1)
                species = [s.strip() for s in species_list.split(",")]
                groupings[group_name] = species
            except ValueError:
                logger.error(f"Invalid group format: {group_spec}. Use GroupName:Species1,Species2,...")
                sys.exit(1)
    
    try:
        check_dependencies(['mafft', 'iqtree3'], logger)
        seq_tuples = read_sequences_from_file(args.input_file, logger)
        if len(seq_tuples) < 3:
            logger.error("At least 3 sequences are required for phylogenetic analysis")
            sys.exit(1)
        if args.seq_type is None:
            sequences = [seq for _, seq in seq_tuples]
            seq_type = detect_sequence_type(sequences, logger)
        else:
            seq_type = args.seq_type
            logger.info(f"Using user-specified sequence type: {seq_type}")
        mafft_success = run_mafft(args.input_file, args.alignment_file, args.threads, logger)
        if not mafft_success:
            logger.error("MAFFT alignment failed")
            sys.exit(1)
        # Run IQ-TREE and handle the result
        iqtree_tree_file = None  # Initialize to None to handle any unexpected exceptions
        try:
            iqtree_tree_file = run_iqtree(args.alignment_file, seq_type, args.bootstrap, args.threads, logger)
        except Exception as e:
            logger.error(f"IQ-TREE run failed: {e}")
            sys.exit(1)
            
        if iqtree_tree_file and os.path.exists(iqtree_tree_file):
            shutil.move(iqtree_tree_file, args.tree_file)
            logger.info(f"Final tree file saved to {args.tree_file}")
        else:
            logger.error("IQ-TREE did not produce a tree file or the file does not exist")
            sys.exit(1)
        viz_success = visualize_tree_circular(args.tree_file, args.output, groupings, logger)
        if not viz_success:
            logger.error("Visualization failed")
            sys.exit(1)
        if not args.keep_all_files:
            keep = {args.output, args.tree_file}
            prefix = str(Path(args.alignment_file).with_suffix(''))
            iqtree_extensions = ['.log', '.iqtree', '.bionj', '.mldist', '.model.gz', '.ckp.gz', '.ufboot', '.contree']
            if args.alignment_file not in keep and os.path.exists(args.alignment_file):
                os.unlink(args.alignment_file)
                logger.info(f"Removed: {args.alignment_file}")
            cleanup_files(prefix, iqtree_extensions, keep, logger)
        logger.info("Analysis completed successfully!")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)