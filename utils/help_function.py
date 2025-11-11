#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
import sys
import shutil
from Bio import SeqIO
from omegaconf import DictConfig

def show_help_with_rich(cfg: DictConfig = None):
    """Display enhanced help information using rich."""
    console = Console()
    
    # Use default values if config is not provided
    app_name = "pyPhyTrees" if cfg is None or 'software' not in cfg or 'app_name' not in cfg.software else cfg.software.app_name
    version = "v1.0" if cfg is None or 'software' not in cfg or 'version' not in cfg.software else cfg.software.version
    description = "Phylogenetic Tree Construction and Visualization Tool" if cfg is None or 'software' not in cfg or 'description' not in cfg.software else cfg.software.description
    
    console.print(Panel(
        f"[bold yellow]{app_name}[/bold yellow]: {description}\n\n"
        "[cyan]Description:[/cyan]\n"
        "  This script automates the process of phylogenetic tree construction by:\n"
        "  • Aligning sequences using MAFFT\n"
        "  • Building phylogenetic trees with IQ-TREE\n"
        "  • Creating visualizations with PyCirclize\n\n"
        
        "[cyan]Dependencies:[/cyan]\n"
        "  • [bold]MAFFT[/bold] - Multiple sequence alignment tool\n"
        "  • [bold]IQ-TREE[/bold] - Phylogenetic tree inference software\n"
        "  • [bold]PyCirclize[/bold] - Circular visualization library\n\n"
        
        "[cyan]Usage Examples:[/cyan]\n"
        "  [bold white]Build tree from sequences:[/bold white]\n"
        "    python main.py build sequences.fasta\n\n"
        
        "  [bold white]Build with custom parameters:[/bold white]\n"
        "    python main.py build sequences.fasta -o my_tree.png --seq-type dna -B 1000 --threads 4\n\n"
        
        "  [bold white]Build with grouping for visualization:[/bold white]\n"
        "    python main.py build sequences.fasta -g 'Group1:seq1,seq2' -g 'Group2:seq3,seq4'\n\n"
        
        "  [bold white]Plot tree from existing tree file:[/bold white]\n"
        "    python main.py plot tree.nwk -o my_tree.png\n\n",
        
        title=f"[bold green]{app_name} Help[/bold green]",
        border_style="green",
        expand=False
    ))
    
    # Create a table for arguments
    table = Table(title="Available Arguments", show_header=True, header_style="bold magenta")
    table.add_column("Argument", style="cyan", width=20)
    table.add_column("Description", style="white")
    table.add_column("Default", style="yellow")
    
    table.add_row("build", "Build phylogenetic tree from sequences", "")
    table.add_row("plot", "Plot phylogenetic tree from existing tree file", "")
    table.add_row("INPUT_FILE", "Input FASTA file containing sequences (for build command)", "")
    table.add_row("TREE_FILE", "Input tree file in Newick format (for plot command)", "")
    table.add_row("-o, --output", "Output image file name", "phylogenetic_tree_circular.png")
    table.add_row("--tree-file", "Output tree file in Newick format", "tree.nwk")
    table.add_row("--alignment-file", "Output alignment file in FASTA format", "aligned.fasta")
    table.add_row("--seq-type", "Sequence type (auto-detected if not provided)", "auto")
    table.add_row("-B, --bootstrap", "Number of Ultrafast Bootstrap replicates for IQ-TREE", "100")
    table.add_row("--threads", "Number of threads to use for MAFFT and IQ-TREE", "1")
    table.add_row("-g, --group", "Group species for visualization (format: GroupName:Species1,Species2,...)", "")
    table.add_row("--visualization-style", "Type of visualization to generate (circular, rectangular, radial, heatmap, all)", "circular")
    table.add_row("--keep-all-files", "Keep all intermediate files (alignment, logs, etc.)", "False")
    
    console.print(table)

def check_dependencies(tools, logger=None):
    # If no logger is provided, create a simple output function
    if logger is None:
        def logger_info(msg):
            print(f"[INFO] {msg}")
        def logger_error(msg):
            print(f"[ERROR] {msg}")
        logger = type('Logger', (), {'info': logger_info, 'error': logger_error})()
    
    for tool in tools:
        if shutil.which(tool) is None:
            logger.error(f"Error: Required tool '{tool}' not found in PATH.")
            logger.error(f"Please install it (e.g., 'conda install -c bioconda {tool}') and try again.")
            raise FileNotFoundError(f"Dependency not found: {tool}")
    logger.info("All external dependencies (MAFFT, IQ-TREE) are available.")

def read_sequences_from_file(file_path, logger=None):
    # If no logger is provided, create a simple output function
    if logger is None:
        def logger_info(msg):
            print(f"[INFO] {msg}")
        def logger_error(msg):
            print(f"[ERROR] {msg}")
        logger = type('Logger', (), {'info': logger_info, 'error': logger_error})()
        
    sequences = []
    try:
        with open(file_path, 'r') as handle:
            for record in SeqIO.parse(handle, "fasta"):
                sequences.append((record.id, str(record.seq)))
        logger.info(f"Successfully read {len(sequences)} sequences from {file_path}")
        return sequences
    except Exception as e:
        logger.error(f"Error reading sequences from {file_path}: {e}")
        raise

# Define the logo function
def show_logo(cfg: DictConfig = None):
    """Display a fancy logo for the script using rich."""
    # Use default values if config is not provided
    version = "v1.0" if cfg is None or 'software' not in cfg or 'version' not in cfg.software else cfg.software.version
    app_name = "pyPhyTrees" if cfg is None or 'software' not in cfg or 'app_name' not in cfg.software else cfg.software.app_name
    description = "Phylogenetic Tree Construction Tool" if cfg is None or 'software' not in cfg or 'description' not in cfg.software else cfg.software.description
    
    console = Console()
    logo_text = Text.from_markup(
        f"[bold blue]╔══════════════════════════════════════════════════════════════╗\n"
        f"[bold blue]║                    [green]{app_name}[/green] [blue]{version}[/blue]                    ║\n"
        "║                                                              ║\n"
        f"║         [bold white]{description}[/bold white]          ║\n"
        "║        [italic]Build & Visualize Evolutionary Relationships[/italic]        ║\n"
        "║                                                              ║\n"
        "║           [bold green]MAFFT[/bold green] + [bold green]IQ-TREE[/bold green] + [bold green]PyCirclize[/bold green] = ❤️           ║\n"
        "[bold blue]╚══════════════════════════════════════════════════════════════╝[/bold blue]"
    )
    console.print(logo_text)
    console.print()