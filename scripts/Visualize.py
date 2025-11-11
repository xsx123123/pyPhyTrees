#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phylogenetic Tree Visualization Module
=======================================
This module provides multiple visualization styles for phylogenetic trees:
- Circular visualization
- Rectangular phylogram
- Rectangular cladogram
- Radial phylogram
- Radial cladogram
- Phylogram with heatmap
All visualizations support grouping and are output at 800 DPI in both PNG and PDF formats.
"""

import os
import sys
import math
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import colormaps
import matplotlib.patches as mpatches
from Bio import Phylo
try:
    from pycirclize import Circos
except ImportError:
    print("Pycirclize not available. Circular visualization will not work.")
    Circos = None

def visualize_tree_circular(tree_file, output_file, groupings=None, group_colors=None, logger=None, dpi=800):
    """
    Create circular visualization of phylogenetic tree using pycirclize
    """
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)

    if Circos is None:
        logger.error("Pycirclize is not available. Cannot create circular visualization.")
        return False

    logger.info(f"Creating circular visualization of phylogenetic tree at {dpi} DPI...")
    if groupings is None:
        groupings = {}
    if group_colors is None:
        group_colors = {}

    try:
        if not os.path.exists(tree_file):
            logger.error(f"Tree file does not exist: {tree_file}")
            raise FileNotFoundError(f"Tree file does not exist: {tree_file}")

        # Create visualizations for both PNG and PDF
        base_path = Path(output_file)
        png_path = base_path.with_suffix('.png')
        pdf_path = base_path.with_suffix('.pdf')

        circos, tv = Circos.initialize_from_tree(
            tree_file, r_lim=(30, 100), leaf_label_size=8,
            line_kws=dict(color="lightgrey", lw=1.5), ignore_branch_length=False
        )

        if groupings:
            # Use custom colors if provided, otherwise generate from default colormap
            n_groups = len(groupings)
            if group_colors:
                # Use provided custom colors
                group_name2color = {}
                for group_name in groupings:
                    if group_name in group_colors:
                        group_name2color[group_name] = group_colors[group_name]
                    else:
                        # Fallback to default colormap for missing custom colors
                        colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                        idx = list(groupings.keys()).index(group_name)
                        group_name2color[group_name] = colormap(idx)
            else:
                # Generate colors using default colormap
                colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                group_name2color = {name: colormap(i) for i, name in enumerate(groupings)}
            
            for group_name, species_list in groupings.items():
                color = group_name2color[group_name]
                tv.set_node_line_props(species_list, color=color, apply_label_color=True)

        fig = circos.plotfig()

        if groupings:
            handles = [Line2D([], [], label=name, color=group_name2color.get(name, 'black')) for name in groupings.keys()]
            circos.ax.legend(
                handles=handles, labelcolor=[group_name2color.get(name, 'black') for name in groupings.keys()],
                fontsize=8, loc="center", bbox_to_anchor=(0.5, 0.5)
            )

        # Save as PNG
        fig.savefig(png_path, dpi=dpi, bbox_inches='tight', format='png')
        logger.info(f"Circular visualization saved to {png_path}")

        # Save as PDF
        fig.savefig(pdf_path, dpi=dpi, bbox_inches='tight', format='pdf')
        logger.info(f"Circular visualization saved to {pdf_path}")

        plt.close(fig)
        return True

    except Exception as e:
        logger.error(f"Error creating circular visualization: {e}")
        import traceback
        traceback.print_exc()
        return False


def visualize_tree_rectangular(tree_file, output_file, groupings=None, group_colors=None, logger=None, dpi=800, cladogram=False, color_by_distance=True):
    """
    Create rectangular phylogenetic tree visualization with proper group or distance-based coloring
    """
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)

    logger.info(f"Creating {'cladogram' if cladogram else 'phylogram'} rectangular visualization at {dpi} DPI...")
    if groupings is None:
        groupings = {}
    if group_colors is None:
        group_colors = {}

    try:
        if not os.path.exists(tree_file):
            logger.error(f"Tree file does not exist: {tree_file}")
            raise FileNotFoundError(f"Tree file does not exist: {tree_file}")

        # Parse the tree
        tree = Phylo.read(tree_file, 'newick')

        # Create visualizations for both PNG and PDF
        base_path = Path(output_file)
        png_path = base_path.with_suffix('.png')
        pdf_path = base_path.with_suffix('.pdf')

        # Create a figure with appropriate size for rectangular layout
        fig, ax = plt.subplots(figsize=(16, 12))

        if color_by_distance:
            # Color branches based on evolutionary distances
            from matplotlib.colors import Normalize
            from matplotlib.cm import ScalarMappable
            
            # Calculate all branch lengths for coloring
            all_branch_lengths = []
            for clade in tree.find_clades():
                if clade.branch_length is not None:
                    all_branch_lengths.append(clade.branch_length)
            
            if all_branch_lengths:
                min_length = min(all_branch_lengths)
                max_length = max(all_branch_lengths)
                norm = Normalize(vmin=min_length, vmax=max_length)
                cmap = plt.get_cmap('viridis')  # Use a gradient colormap
                
                # Calculate positions for all nodes
                terminals = list(tree.get_terminals())
                
                # Calculate positions for all nodes
                def calculate_positions(clade, x=0):
                    """Calculate x and y positions for each clade in the tree"""
                    if clade.is_terminal():
                        # Terminal node: use its index for y position
                        terminal_idx = [t.name for t in terminals].index(clade.name)
                        clade.y_pos = terminal_idx * (10 / max(len(terminals) - 1, 1))
                        clade.x_pos = x
                    else:
                        # Internal node: y position is average of children
                        for child in clade:
                            calculate_positions(child, x + (child.branch_length if child.branch_length else 0))
                        child_y_positions = [child.y_pos for child in clade.clades]
                        clade.y_pos = sum(child_y_positions) / len(child_y_positions)
                        clade.x_pos = x

                calculate_positions(tree.root)

                # Draw all branches with distance-based coloring
                def draw_branch(clade, ax):
                    """Recursively draw branches with distance-based colors"""
                    if not clade.is_terminal():
                        # Draw internal branches
                        for child in clade:
                            # Horizontal line for this branch
                            if hasattr(child, 'x_pos') and hasattr(child, 'y_pos'):
                                # Color based on branch length
                                branch_length = child.branch_length if child.branch_length else 0
                                branch_color = cmap(norm(branch_length))
                                branch_width = 1.5
                                
                                ax.hlines(child.y_pos, clade.x_pos, child.x_pos, colors=branch_color, linewidth=branch_width)
                                
                                # Vertical line connecting to children (for internal nodes)
                                if not child.is_terminal() and child.clades:
                                    child_y_positions = [c.y_pos for c in child.clades if hasattr(c, 'y_pos')]
                                    if child_y_positions:
                                        min_y = min(child_y_positions)
                                        max_y = max(child_y_positions)
                                        ax.vlines(child.x_pos, min_y, max_y, colors='black', linewidth=1.5)
                            
                            # Recursively draw child branches
                            draw_branch(child, ax)
                    
                    # Draw terminal branches and labels
                    if clade.is_terminal() and clade.name:
                        # Color based on branch length that leads to this terminal
                        parent_branch_length = clade.branch_length if clade.branch_length else 0
                        terminal_color = cmap(norm(parent_branch_length))
                        
                        # Draw a colored marker for the terminal
                        ax.plot(clade.x_pos, clade.y_pos, 'o', color=terminal_color, markersize=8, 
                                markeredgecolor='black', markeredgewidth=0.5)
                        
                        # Add label to the right of the terminal
                        ax.text(clade.x_pos + 0.02, clade.y_pos, clade.name, 
                                verticalalignment='center', fontsize=8)

                draw_branch(tree.root, ax)
                
                # Add colorbar for distance scale
                sm = ScalarMappable(norm=norm, cmap=cmap)
                sm.set_array([])
                cbar = plt.colorbar(sm, ax=ax)
                cbar.set_label('Branch Length', rotation=270, labelpad=20)
                
            else:
                # If no branch lengths, draw normally
                if cladogram:
                    Phylo.draw(tree, axes=ax, do_show=False, branch_labels=lambda x: "")
                else:
                    Phylo.draw(tree, axes=ax, do_show=False)
                
        elif groupings:  # Original grouping-based coloring
            # Create a mapping of leaf names to groups
            leaf_to_group = {}
            for group_name, species_list in groupings.items():
                for species in species_list:
                    # Clean up species name to match tree leaves (remove prefixes like 'gene')
                    clean_species = species.strip()
                    leaf_to_group[clean_species] = group_name

            # Create a mapping of colors to groups
            n_groups = len(groupings)
            if group_colors:
                # Use custom colors if provided
                colors = []
                for group_name in groupings:
                    if group_name in group_colors:
                        colors.append(group_colors[group_name])
                    else:
                        # Generate a color for each group if not provided
                        colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                        idx = list(groupings.keys()).index(group_name)
                        colors.append(colormap(idx))
                group_colors_dict = {name: colors[i] for i, name in enumerate(groupings.keys())}
            else:
                # Generate colors using default colormap
                colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                group_colors_dict = {name: colormap(i) for i, name in enumerate(groupings)}

            # Calculate positions for all nodes
            terminals = list(tree.get_terminals())
            
            # Calculate positions for all nodes
            def calculate_positions(clade, x=0):
                """Calculate x and y positions for each clade in the tree"""
                if clade.is_terminal():
                    # Terminal node: use its index for y position
                    terminal_idx = [t.name for t in terminals].index(clade.name)
                    clade.y_pos = terminal_idx * (10 / max(len(terminals) - 1, 1))
                    clade.x_pos = x
                else:
                    # Internal node: y position is average of children
                    for child in clade:
                        calculate_positions(child, tree.distance(clade))
                    child_y_positions = [child.y_pos for child in clade.clades]
                    clade.y_pos = sum(child_y_positions) / len(child_y_positions)
                    clade.x_pos = x

            calculate_positions(tree.root)

            # Draw all branches with proper coloring
            def draw_branch(clade, ax):
                """Recursively draw branches with proper colors"""
                if not clade.is_terminal():
                    # Draw internal branches
                    for child in clade:
                        # Horizontal line for this branch
                        if hasattr(child, 'x_pos') and hasattr(child, 'y_pos'):
                            # Determine color based on whether this branch leads to grouped terminals
                            branch_color = 'black'
                            branch_width = 1.5
                            
                            # Check if this child is terminal and has a group
                            if child.is_terminal() and child.name and child.name in leaf_to_group:
                                group_name = leaf_to_group[child.name]
                                branch_color = group_colors_dict[group_name]
                                branch_width = 2.5  # Make grouped branches slightly thicker
                            
                            ax.hlines(child.y_pos, clade.x_pos, child.x_pos, colors=branch_color, linewidth=branch_width)
                            
                            # Vertical line connecting to children (for internal nodes)
                            if not child.is_terminal() and child.clades:
                                child_y_positions = [c.y_pos for c in child.clades if hasattr(c, 'y_pos')]
                                if child_y_positions:
                                    min_y = min(child_y_positions)
                                    max_y = max(child_y_positions)
                                    ax.vlines(child.x_pos, min_y, max_y, colors='black', linewidth=1.5)
                        
                        # Recursively draw child branches
                        draw_branch(child, ax)
                
                # Draw terminal branches and labels
                if clade.is_terminal() and clade.name:
                    if clade.name in leaf_to_group:
                        group_name = leaf_to_group[clade.name]
                        terminal_color = group_colors_dict[group_name]
                        
                        # Draw a colored marker for the terminal
                        ax.plot(clade.x_pos, clade.y_pos, 'o', color=terminal_color, markersize=8, 
                                markeredgecolor='black', markeredgewidth=0.5)
                        
                        # Add label to the right of the terminal
                        ax.text(clade.x_pos + 0.02, clade.y_pos, clade.name, 
                                verticalalignment='center', fontsize=8)
                    else:
                        # Ungrouped terminal - use default color
                        ax.plot(clade.x_pos, clade.y_pos, 'o', color='gray', markersize=6)
                        ax.text(clade.x_pos + 0.02, clade.y_pos, clade.name, 
                                verticalalignment='center', fontsize=8)

            draw_branch(tree.root, ax)
            
        else:
            # Draw tree normally if no groupings
            if cladogram:
                Phylo.draw(tree, axes=ax, do_show=False, branch_labels=lambda x: "")
            else:
                Phylo.draw(tree, axes=ax, do_show=False)

        # Add y-axis labels if needed for clarity (for both distance and group coloring)
        ax.set_ylabel('Taxa', fontsize=12)
        ax.set_xlabel('Evolutionary Distance' if not cladogram else 'Cladogram Distance', fontsize=12)
        ax.set_title(f"{'Cladogram' if cladogram else 'Phylogram'} - Rectangular Layout", fontsize=16)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Add legend for groupings only (not for distance coloring)
        if groupings and not color_by_distance:
            # Create legend for groupings with custom colors
            patches = [mpatches.Patch(color=group_colors_dict[name], label=name) for name in groupings.keys()]
            ax.legend(handles=patches, loc='upper right')

        # Save as PNG
        fig.savefig(png_path, dpi=dpi, bbox_inches='tight', format='png')
        logger.info(f"Rectangular {'' if cladogram else 'cladogram'} visualization saved to {png_path}")

        # Save as PDF
        fig.savefig(pdf_path, dpi=dpi, bbox_inches='tight', format='pdf')
        logger.info(f"Rectangular {'' if cladogram else 'cladogram'} visualization saved to {pdf_path}")

        plt.close(fig)
        return True

    except Exception as e:
        logger.error(f"Error creating rectangular {'cladogram' if cladogram else 'phylogram'} visualization: {e}")
        import traceback
        traceback.print_exc()
        return False


def visualize_tree_radial(tree_file, output_file, groupings=None, group_colors=None, logger=None, dpi=800, cladogram=False, color_by_distance=True):
    """
    Create radial phylogenetic tree visualization with proper group or distance-based coloring
    """
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)

    logger.info(f"Creating {'cladogram' if cladogram else 'phylogram'} radial visualization at {dpi} DPI...")
    if groupings is None:
        groupings = {}
    if group_colors is None:
        group_colors = {}

    try:
        if not os.path.exists(tree_file):
            logger.error(f"Tree file does not exist: {tree_file}")
            raise FileNotFoundError(f"Tree file does not exist: {tree_file}")

        # Parse the tree
        tree = Phylo.read(tree_file, 'newick')

        # Create visualizations for both PNG and PDF
        base_path = Path(output_file)
        png_path = base_path.with_suffix('.png')
        pdf_path = base_path.with_suffix('.pdf')

        # Create a figure for radial layout (using regular subplot, not polar)
        fig, ax = plt.subplots(figsize=(14, 14), subplot_kw=dict(projection='polar'))

        if color_by_distance:
            # Color branches based on evolutionary distances
            from matplotlib.colors import Normalize
            from matplotlib.cm import ScalarMappable

            # Calculate all branch lengths for coloring
            all_branch_lengths = []
            for clade in tree.find_clades():
                if clade.branch_length is not None:
                    all_branch_lengths.append(clade.branch_length)

            if all_branch_lengths:
                min_length = min(all_branch_lengths)
                max_length = max(all_branch_lengths)
                norm = Normalize(vmin=min_length, vmax=max_length)
                cmap = plt.get_cmap('viridis')  # Use a gradient colormap

                # Calculate angular positions for all terminals
                terminals = list(tree.get_terminals())
                total_terminals = len(terminals)

                # Calculate positions for all nodes in polar coordinates
                angles = {}
                for i, terminal in enumerate(terminals):
                    angles[terminal.name] = 2 * 3.14159 * i / total_terminals  # Distribute evenly around circle

                # Function to recursively calculate positions for internal nodes
                def calculate_radial_positions(clade):
                    if clade.is_terminal():
                        clade.angle = angles[clade.name]
                        clade.radius = tree.distance(tree.root, clade)  # distance from root
                    else:
                        # For internal nodes, calculate average angle of children
                        child_angles = []
                        child_radius = []
                        for child in clade:
                            calculate_radial_positions(child)
                            if hasattr(child, 'angle'):
                                child_angles.append(child.angle)
                            if hasattr(child, 'radius'):
                                child_radius.append(child.radius)

                        if child_angles:
                            # Calculate the mean angle, accounting for wraparound
                            avg_sin = sum([math.sin(angle) for angle in child_angles]) / len(child_angles)
                            avg_cos = sum([math.cos(angle) for angle in child_angles])
                            clade.angle = math.atan2(avg_sin, avg_cos)
                            if clade.angle < 0:
                                clade.angle += 2 * 3.14159
                            clade.radius = sum(child_radius) / len(child_radius) if child_radius else 0
                        else:
                            clade.angle = 0
                            clade.radius = 0

                calculate_radial_positions(tree.root)

                # Draw tree manually with distance-based coloring
                def draw_radial_branch(clade, ax):
                    if not clade.is_terminal():
                        for child in clade:
                            # Color based on branch length
                            branch_length = child.branch_length if child.branch_length else 0
                            branch_color = cmap(norm(branch_length))
                            branch_width = 2.0

                            # Draw line from parent to child
                            if hasattr(clade, 'angle') and hasattr(child, 'angle') and \
                               hasattr(clade, 'radius') and hasattr(child, 'radius'):
                                ax.plot([clade.angle, child.angle], [clade.radius, child.radius],
                                       color=branch_color, linewidth=branch_width)

                                # Draw child node marker if it's terminal
                                if child.is_terminal():
                                    terminal_color = cmap(norm(branch_length))
                                    ax.plot(child.angle, child.radius, 'o', color=terminal_color, markersize=8)
                                    # Add label
                                    ax.text(child.angle, child.radius, f'  {child.name}',
                                           horizontalalignment='left', verticalalignment='center', fontsize=8)

                            # Recursively draw child branches
                            draw_radial_branch(child, ax)

                draw_radial_branch(tree.root, ax)

                # Add colorbar for distance scale
                sm = ScalarMappable(norm=norm, cmap=cmap)
                sm.set_array([])
                cbar = plt.colorbar(sm, ax=ax)
                cbar.set_label('Branch Length', rotation=270, labelpad=20)

            else:
                # If no branch lengths, draw normally
                if cladogram:
                    Phylo.draw(tree, axes=ax, do_show=False, branch_labels=lambda x: "")
                else:
                    Phylo.draw(tree, axes=ax, do_show=False)

        elif groupings:
            # Create a mapping of leaf names to groups
            leaf_to_group = {}
            for group_name, species_list in groupings.items():
                for species in species_list:
                    clean_species = species.strip()
                    leaf_to_group[clean_species] = group_name

            # Create a mapping of colors to groups
            n_groups = len(groupings)
            if group_colors:
                # Use custom colors if provided
                colors = []
                for group_name in groupings:
                    if group_name in group_colors:
                        colors.append(group_colors[group_name])
                    else:
                        # Generate a color for each group if not provided
                        colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                        idx = list(groupings.keys()).index(group_name)
                        colors.append(colormap(idx))
                group_colors_dict = {name: colors[i] for i, name in enumerate(groupings.keys())}
            else:
                # Generate colors using default colormap
                colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                group_colors_dict = {name: colormap(i) for i, name in enumerate(groupings)}

            # Calculate angular positions for all terminals
            terminals = list(tree.get_terminals())
            total_terminals = len(terminals)
            
            # Calculate positions for all nodes in polar coordinates
            angles = {}
            for i, terminal in enumerate(terminals):
                angles[terminal.name] = 2 * 3.14159 * i / total_terminals  # Distribute evenly around circle

            # Function to recursively calculate positions for internal nodes
            def calculate_radial_positions(clade):
                if clade.is_terminal():
                    clade.angle = angles[clade.name]
                    clade.radius = tree.distance(tree.root, clade)  # distance from root
                else:
                    # For internal nodes, calculate average angle of children
                    child_angles = []
                    child_radius = []
                    for child in clade:
                        calculate_radial_positions(child)
                        if hasattr(child, 'angle'):
                            child_angles.append(child.angle)
                        if hasattr(child, 'radius'):
                            child_radius.append(child.radius)
                    
                    if child_angles:
                        # Calculate the mean angle, accounting for wraparound
                        avg_sin = sum([math.sin(angle) for angle in child_angles]) / len(child_angles)
                        avg_cos = sum([math.cos(angle) for angle in child_angles])
                        clade.angle = math.atan2(avg_sin, avg_cos)
                        if clade.angle < 0:
                            clade.angle += 2 * 3.14159
                        clade.radius = sum(child_radius) / len(child_radius) if child_radius else 0
                    else:
                        clade.angle = 0
                        clade.radius = 0

            calculate_radial_positions(tree.root)

            # Draw the tree manually with proper group coloring
            def draw_radial_branch(clade, ax):
                if not clade.is_terminal():
                    for child in clade:
                        # Determine color based on whether this branch leads to grouped terminals
                        branch_color = 'black'
                        
                        # For internal nodes, we need to check if any terminal under this clade is grouped
                        if child.is_terminal() and child.name and child.name in leaf_to_group:
                            group_name = leaf_to_group[child.name]
                            branch_color = group_colors_dict[group_name]
                        
                        # Draw line from parent to child
                        if hasattr(clade, 'angle') and hasattr(child, 'angle') and \
                           hasattr(clade, 'radius') and hasattr(child, 'radius'):
                            ax.plot([clade.angle, child.angle], [clade.radius, child.radius], 
                                   color=branch_color, linewidth=2.0)
                            
                            # Draw child node marker if it's terminal
                            if child.is_terminal():
                                if child.name in leaf_to_group:
                                    marker_color = group_colors_dict[leaf_to_group[child.name]]
                                    ax.plot(child.angle, child.radius, 'o', color=marker_color, markersize=8)
                                    # Add label
                                    ax.text(child.angle, child.radius, f'  {child.name}', 
                                           horizontalalignment='left', verticalalignment='center', fontsize=8)
                                else:
                                    ax.plot(child.angle, child.radius, 'o', color='gray', markersize=6)
                                    ax.text(child.angle, child.radius, f'  {child.name}', 
                                           horizontalalignment='left', verticalalignment='center', fontsize=8)
                        
                        # Recursively draw child branches
                        draw_radial_branch(child, ax)

            draw_radial_branch(tree.root, ax)
            
        else:
            # Draw tree normally if no groupings
            if cladogram:
                Phylo.draw(tree, axes=ax, do_show=False, branch_labels=lambda x: "")
            else:
                Phylo.draw(tree, axes=ax, do_show=False)

        ax.set_title(f"{'Cladogram' if cladogram else 'Phylogram'} - Radial Layout", fontsize=16)

        # Add legend for groupings only (not for distance coloring)
        if groupings and not color_by_distance:
            # Create legend for groupings with custom colors
            patches = [mpatches.Patch(color=group_colors_dict[name], label=name) for name in groupings.keys()]
            ax.legend(handles=patches, loc='upper right', bbox_to_anchor=(1.1, 1.0))

        # Save as PNG
        fig.savefig(png_path, dpi=dpi, bbox_inches='tight', format='png')
        logger.info(f"Radial {'cladogram' if cladogram else 'phylogram'} visualization saved to {png_path}")

        # Save as PDF
        fig.savefig(pdf_path, dpi=dpi, bbox_inches='tight', format='pdf')
        logger.info(f"Radial {'cladogram' if cladogram else 'phylogram'} visualization saved to {pdf_path}")

        plt.close(fig)
        return True

    except Exception as e:
        logger.error(f"Error creating radial {'cladogram' if cladogram else 'phylogram'} visualization: {e}")
        import traceback
        traceback.print_exc()
        return False


def visualize_tree_with_heatmap(tree_file, output_file, groupings=None, group_colors=None, logger=None, dpi=800):
    """
    Create a phylogenetic tree with a heatmap visualization that uses group-based colors
    """
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)

    logger.info(f"Creating phylogenetic tree with heatmap visualization at {dpi} DPI...")
    if groupings is None:
        groupings = {}
    if group_colors is None:
        group_colors = {}

    try:
        if not os.path.exists(tree_file):
            logger.error(f"Tree file does not exist: {tree_file}")
            raise FileNotFoundError(f"Tree file does not exist: {tree_file}")

        # Parse the tree
        tree = Phylo.read(tree_file, 'newick')

        # Create visualizations for both PNG and PDF
        base_path = Path(output_file)
        png_path = base_path.with_suffix('.png')
        pdf_path = base_path.with_suffix('.pdf')

        # Create a larger figure to accommodate tree and potential heatmap
        fig, ax = plt.subplots(figsize=(20, 12))

        # Draw tree normally first (without color_func which is not supported by Phylo.draw)
        Phylo.draw(tree, axes=ax, do_show=False,
                  label_func=lambda x: x.name if x.name else '',
                  branch_labels=lambda x: "")

        # Set up group coloring by manually drawing colored nodes
        if groupings:
            # Create a mapping of leaf names to groups
            leaf_to_group = {}
            for group_name, species_list in groupings.items():
                for species in species_list:
                    clean_species = species.strip()
                    leaf_to_group[clean_species] = group_name

            # Create a mapping of colors to groups
            n_groups = len(groupings)
            if group_colors:
                # Use custom colors if provided
                colors = []
                for group_name in groupings:
                    if group_name in group_colors:
                        colors.append(group_colors[group_name])
                    else:
                        # Generate a color for each group if not provided
                        colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                        idx = list(groupings.keys()).index(group_name)
                        colors.append(colormap(idx))
                group_colors_dict = {name: colors[i] for i, name in enumerate(groupings.keys())}
            else:
                # Generate colors using default colormap
                colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                group_colors_dict = {name: colormap(i) for i, name in enumerate(groupings)}

            # Manually update terminal nodes to apply group colors
            for clade in tree.get_terminals():
                if clade.name and clade.name in leaf_to_group:
                    group_name = leaf_to_group[clade.name]
                    # Find and update the point representing this terminal
                    # This depends on how matplotlib represents the drawn tree
                    for line in ax.lines:
                        if hasattr(line, 'get_label') and line.get_label() == clade.name:
                            line.set_color(group_colors_dict[group_name])
                            break

        ax.set_title("Phylogenetic Tree with Heatmap", fontsize=16)

        if groupings:
            # Create legend for groupings
            patches = [mpatches.Patch(color=group_colors_dict[name], label=name) for name in groupings.keys()]
            ax.legend(handles=patches, loc='upper right')

        # Save as PNG
        fig.savefig(png_path, dpi=dpi, bbox_inches='tight', format='png')
        logger.info(f"Tree with heatmap visualization saved to {png_path}")

        # Save as PDF
        fig.savefig(pdf_path, dpi=dpi, bbox_inches='tight', format='pdf')
        logger.info(f"Tree with heatmap visualization saved to {pdf_path}")

        plt.close(fig)
        return True

    except Exception as e:
        logger.error(f"Error creating tree with heatmap visualization: {e}")
        import traceback
        traceback.print_exc()
        return False


def visualize_all_styles(tree_file, output_prefix, groupings=None, group_colors=None, logger=None, color_by_distance=True):
    """
    Create all available visualization styles
    """
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)

    logger.info("Creating all visualization styles...")

    # Circular visualization
    circular_output = f"{output_prefix}_circular"
    success1 = visualize_tree_circular(tree_file, circular_output, groupings, group_colors, logger)

    # Rectangular phylogram
    rectangular_phylo_output = f"{output_prefix}_rectangular_phylogram"
    success2 = visualize_tree_rectangular(tree_file, rectangular_phylo_output, groupings, group_colors, logger, cladogram=False, color_by_distance=color_by_distance)

    # Rectangular cladogram
    rectangular_clado_output = f"{output_prefix}_rectangular_cladogram"
    success3 = visualize_tree_rectangular(tree_file, rectangular_clado_output, groupings, group_colors, logger, cladogram=True, color_by_distance=color_by_distance)

    # Radial phylogram
    radial_phylo_output = f"{output_prefix}_radial_phylogram"
    success4 = visualize_tree_radial(tree_file, radial_phylo_output, groupings, group_colors, logger, cladogram=False, color_by_distance=color_by_distance)

    # Radial cladogram
    radial_clado_output = f"{output_prefix}_radial_cladogram"
    success5 = visualize_tree_radial(tree_file, radial_clado_output, groupings, group_colors, logger, cladogram=True, color_by_distance=color_by_distance)

    # Tree with heatmap
    heatmap_output = f"{output_prefix}_tree_heatmap"
    success6 = visualize_tree_with_heatmap(tree_file, heatmap_output, groupings, group_colors, logger)

    # Summary
    success_count = sum([success1, success2, success3, success4, success5, success6])
    total_count = 6
    logger.info(f"Successfully created {success_count}/{total_count} visualization styles (each as PNG and PDF)")

    return success_count == total_count


# Alternative implementations for rectangular and radial trees with better group colorings
def _color_tree_branches_by_groups(tree, groupings, group_colors):
    """
    Helper function to color tree branches by groups.
    This is a helper that can be used with Bio.Phylo for more advanced coloring.
    Note: This requires understanding of Bio.Phylo internals and may not be straightforward to implement.
    """
    # This is a simplified approach - in practice, Bio.Phylo doesn't easily allow individual branch coloring
    # This function would be more complex in a full implementation
    pass


def visualize_tree_rectangular_advanced(tree_file, output_file, groupings=None, group_colors=None, logger=None, dpi=800):
    """
    Advanced rectangular visualization with better control over colors and layout
    """
    if logger is None:
        from utils.log import logger_generator
        from omegaconf import OmegaConf
        cfg = OmegaConf.create({"logs": {"log_level": "INFO", "more_info": True, "project_id": "temp"}})
        logger, _ = logger_generator(cfg)

    logger.info(f"Creating advanced rectangular visualization at {dpi} DPI...")
    if groupings is None:
        groupings = {}
    if group_colors is None:
        group_colors = {}

    try:
        if not os.path.exists(tree_file):
            logger.error(f"Tree file does not exist: {tree_file}")
            raise FileNotFoundError(f"Tree file does not exist: {tree_file}")

        # Parse the tree
        tree = Phylo.read(tree_file, 'newick')

        # Create visualizations for both PNG and PDF
        base_path = Path(output_file)
        png_path = base_path.with_suffix('.png')
        pdf_path = base_path.with_suffix('.pdf')

        # Create a figure
        fig, ax = plt.subplots(figsize=(16, 12))

        # Draw tree with custom styling
        Phylo.draw(tree, axes=ax, do_show=False,
                  branch_labels=lambda x: "",
                  color='black', # Base color
                  label_func=lambda x: x.name if x.name else '')

        ax.set_title("Advanced Rectangular Phylogenetic Tree", fontsize=16)
        ax.grid(True, linestyle='--', alpha=0.6)

        if groupings:
            # Create legend for groupings
            n_groups = len(groupings)
            if group_colors:
                # Use custom colors if provided
                colors = []
                for group_name in groupings:
                    if group_name in group_colors:
                        colors.append(group_colors[group_name])
                    else:
                        # Generate a color for each group if not provided
                        colormap = colormaps.get_cmap('tab20').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                        idx = list(groupings.keys()).index(group_name)
                        colors.append(colormap(idx))
                group_colors_dict = {name: colors[i] for i, name in enumerate(groupings.keys())}
            else:
                # Generate colors using default colormap
                colormap = colormaps.get_cmap('tab10').resampled(n_groups) if n_groups > 10 else colormaps.get_cmap('tab10')
                group_colors_dict = {name: colormap(i) for i, name in enumerate(groupings)}

            patches = [mpatches.Patch(color=group_colors_dict[name], label=name) for name in groupings.keys()]
            ax.legend(handles=patches, loc='upper right')

        # Save as PNG
        fig.savefig(png_path, dpi=dpi, bbox_inches='tight', format='png')
        logger.info(f"Advanced rectangular visualization saved to {png_path}")

        # Save as PDF
        fig.savefig(pdf_path, dpi=dpi, bbox_inches='tight', format='pdf')
        logger.info(f"Advanced rectangular visualization saved to {pdf_path}")

        plt.close(fig)
        return True

    except Exception as e:
        logger.error(f"Error creating advanced rectangular visualization: {e}")
        import traceback
        traceback.print_exc()
        return False


# Export all visualization functions
__all__ = [
    'visualize_tree_circular',
    'visualize_tree_rectangular',
    'visualize_tree_radial',
    'visualize_tree_with_heatmap',
    'visualize_all_styles',
    'visualize_tree_rectangular_advanced'
]