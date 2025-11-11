#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RecombTracer Logo Display Module
================================
This module provides beautiful logo display functionality using rich library.
It can be imported and called from main.py to display the application logo.
"""
import random
from rich import box
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich_gradient import Gradient

try:
    from rich_gradient import Text as GradientText
    GRADIENT_AVAILABLE = True
except ImportError:
    GRADIENT_AVAILABLE = False



class LogoDisplay:
    """
    Logo display class using rich for beautiful terminal output
    """
    GRADIENT_SCHEMES = {
        "sunset": ["#FF0080", "#FF8C00", "#FFD700"],
        "ocean": ["#00CED1", "#1E90FF", "#000080"], 
        "forest": ["#32CD32", "#228B22", "#006400"],
        "fire": ["#FF0000", "#FF4500", "#FFD700"],
        "purple_haze": ["#9370DB", "#8A2BE2", "#4B0082"],
        "rainbow": ["red", "#ff9900", "#ff0", "Lime", "cyan", "blue", "magenta"], 
        "cool_breeze": ["#E0FFFF", "#87CEEB", "#4682B4"], 
        "autumn": ["#FFD700", "#FF8C00", "#DC143C"],
        "neon": ["#39FF14", "#00FFFF", "#FF00FF"], 
        "sakura": ["#FFB7C5", "#FF69B4", "#FF1493"], 
        "midnight": ["#191970", "#4169E1", "#87CEEB"], 
        "lava": ["#8B0000", "#FF4500", "#FFA500"],
        "mint": ["#98FF98", "#00FA9A", "#00CED1"],
        "desert": ["#F4A460", "#D2691E", "#8B4513"],
        "galaxy": ["#483D8B", "#6A5ACD", "#9370DB"],
        "tropical": ["#FF6347", "#FF69B4", "#FFD700"],
        "cyber": ["#00FFFF", "#00FF00", "#FFFF00"],
        "monochrome": ["#FFFFFF", "#808080", "#000000"], 
        "pastel": ["#FFB6C1", "#FFDAB9", "#E0BBE4"],
        "emerald": ["#50C878", "#008B8B", "#006400"]}

    def __init__(self,
                 version: str = "v1.0.0",
                 app_name:str = "RecombTracer",
                 description:str = "Genome Recombination Analysis Tool",
                 rice_color:str = "bold cyan",
                 gradient_colors: list = None,
                 use_gradient: bool = False,
                 gradient_scheme: str = None
                ):
        self.console = Console()
        self.app_name = app_name
        self.version = version
        self.description = description
        self.rice_color = rice_color
        self.use_gradient = use_gradient and GRADIENT_AVAILABLE
        if gradient_scheme == "random":
            scheme_name = random.choice(list(self.GRADIENT_SCHEMES.keys()))
            self.gradient_colors = self.GRADIENT_SCHEMES[scheme_name]
            self.current_scheme = scheme_name
        elif gradient_scheme and gradient_scheme in self.GRADIENT_SCHEMES:
            self.gradient_colors = self.GRADIENT_SCHEMES[gradient_scheme]
            self.current_scheme = gradient_scheme
        elif gradient_colors:
            self.gradient_colors = gradient_colors
            self.current_scheme = "custom"
        else:
            self.gradient_colors = ["cyan", "magenta", "yellow"]
            self.current_scheme = "default"


    def create_ascii_logo(self):
        """
        Defines and randomly returns one of several ASCII logos.
        """
        ascii_type_1 = """
        ▖▖▄▖▖▖▗ ▄▖▄▖▗ ▄▖▄▖
        ▚▘▚ ▚▘▜ ▄▌▄▌▜ ▄▌▄▌
        ▌▌▄▌▌▌▟▖▙▖▄▌▟▖▙▖▄▌
        """
        ascii_type_2 = """
        ██   ██ ███████ ██   ██  ██ ██████  ██████   ██ ██████  ██████  
         ██ ██  ██       ██ ██  ███      ██      ██ ███      ██      ██ 
          ███   ███████   ███    ██  █████   █████   ██  █████   █████  
         ██ ██       ██  ██ ██   ██ ██           ██  ██ ██           ██ 
        ██   ██ ███████ ██   ██  ██ ███████ ██████   ██ ███████ ██████
        """
        ascii_type_3 = """
        ▒██   ██▒  ██████ ▒██   ██▒
        ▒▒ █ █ ▒░▒██    ▒ ▒▒ █ █ ▒░
        ░░  █   ░░ ▓██▄   ░░  █   ░
        ░ █ █ ▒   ▒   ██▒ ░ █ █ ▒ 
        ▒██▒ ▒██▒▒██████▒▒▒██▒ ▒██▒
        ▒▒ ░ ░▓ ░▒ ▒▓▒ ▒ ░▒▒ ░ ░▓ ░
        ░░   ░▒ ░░ ░▒  ░ ░░░   ░▒ ░
        ░    ░  ░  ░  ░   ░    ░  
        ░    ░        ░   ░    ░  
        """                     
        ascii_type_4 = """
        ░█░█░█▀▀░█░█░▀█░░▀▀▄░▀▀█░▀█░░▀▀▄░▀▀█
        ░▄▀▄░▀▀█░▄▀▄░░█░░▄▀░░░▀▄░░█░░▄▀░░░▀▄
        ░▀░▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀▀▀░▀▀░
        """
        ascii_type_5 = """
        __  ______  ___ ____  _____ _ ____  _____ 
        \ \/ / _\ \/ / |___ \|___ // |___ \|___ / 
         \  /\ \ \  /| | __) | |_ \| | __) | |_ \ 
         /  \_\ \/  \| |/ __/ ___) | |/ __/ ___) |
        /_/\_\__/_/\_\_|_____|____/|_|_____|____/ 
        """
        ascii_type_6 = """
        ▗▖  ▗▖ ▗▄▄▖▗▖  ▗▖
         ▝▚▞▘ ▐▌    ▝▚▞▘ 
          ▐▌   ▝▀▚▖  ▐▌  
        ▗▞▘▝▚▖▗▄▄▞▘▗▞▘▝▚▖
        +===============+
        """                      
        ascii_type_7 = """
        ┏┓┏┓┏┓┏┓┏┓┓┏┓┏┓┓┏┓┏┓
         ┃┃ ┗┓ ┃┃ ┃┏┛ ┫┃┏┛ ┫
        ┗┛┗┛┗┛┗┛┗┛┻┗━┗┛┻┗━┗┛
        """
        ascii_type_8 = """
        ██   ██ ███████ ██   ██  ██ ██████  ██████   ██ ██████  ██████  
         ██ ██  ██       ██ ██  ███      ██      ██ ███      ██      ██ 
          ███   ███████   ███    ██  █████   █████   ██  █████   █████  
         ██ ██       ██  ██ ██   ██ ██           ██  ██ ██           ██ 
        ██   ██ ███████ ██   ██  ██ ███████ ██████   ██ ███████ ██████ 
        """
        ascii_type_9 = """
        ╻ ╻┏━┓╻ ╻╺┓ ┏━┓┏━┓╺┓ ┏━┓┏━┓
        ┏╋┛┗━┓┏╋┛ ┃ ┏━┛╺━┫ ┃ ┏━┛╺━┫
        ╹ ╹┗━┛╹ ╹╺┻╸┗━╸┗━┛╺┻╸┗━╸┗━┛
        """
        ascii_type_10 = """
           _     _      _     _      _     _123123
          (c).-.(c)    (c).-.(c)    (c).-.(c)     
           / ._. \      / ._. \      / ._. \      
         __\( Y )/__  __\( Y )/__  __\( Y )/__    
        (_.-/'-'\-._)(_.-/'-'\-._)(_.-/'-'\-._)   
           || X ||      || S ||      || X ||      
         _.' `-' '._  _.' `-' '._  _.' `-' '._    
        (.-./`-'\.-.)(.-./`-`\.-.)(.-./`-'\.-.)   
         `-'     `-'  `-'     `-'  `-'     `-'
         + ==================================== +
        """
        # Create a list of all logos
        all_logos = [
            ascii_type_1,
            ascii_type_2,
            ascii_type_3,
            ascii_type_4,
            ascii_type_5,
            ascii_type_6,
            ascii_type_7,
            ascii_type_8,
            ascii_type_9,
            ascii_type_10
        ]

        return random.choice(all_logos)
    
    def display_welcome_logo(self):
        welcome_text = f"""{self.app_name}:{self.version}\n        {self.description}\n"""
        logo_text = self.create_ascii_logo()
        full_text_content = logo_text + welcome_text
        
        if self.use_gradient:
            text = Gradient(full_text_content, colors=self.gradient_colors)
        else:
            text = Text(full_text_content)
            text.stylize(self.rice_color)
        
        self.console.print(text)
    
    def _print_app_info(self):
        info_text = f"""
        [bold yellow]Version:[/bold yellow] {self.version}
        [bold yellow]Description:[/bold yellow] {self.description}
        """
        info_panel = Panel(
            Text(info_text, style="dim"),
            border_style="dim",
            box=box.SIMPLE,
            width=50
        )
        
        self.console.print(Align.center(info_panel))
    
    def display_mini_logo(self):
        logo_content = f"{self.app_name}:{self.version}"
        
        if self.use_gradient:
            mini_logo = GradientText(logo_content, colors=self.gradient_colors)
        else:
            mini_logo = Text(logo_content, style="bold")
        
        self.console.print(Align.center(mini_logo))

def show_logo(style:str ="welcome",
              version: str = "v1.0.0",
              app_name:str = "RecombTracer",
              description:str = "Genome Recombination Analysis Tool",
              rice_color:str = "bold cyan",
              use_gradient: bool = True,
              gradient_colors: list = None,
              gradient_scheme:str = 'random'
              ) -> None:
    """
    Main entry point function to display a logo.
    """
    logo = LogoDisplay(
        version = version,
        app_name = app_name,
        description = description,
        rice_color = rice_color,
        use_gradient = use_gradient,
        gradient_colors = gradient_colors,
        gradient_scheme = gradient_scheme
    )
    if style == "welcome":
        logo.display_welcome_logo()
    elif style == "mini":
        logo.display_mini_logo()
    
def config2logo(config = None) -> None:
    """
    Extracts information from a config dictionary to show the "welcome" logo.
    """
    # Handle both dict and DictConfig (OmegaConf) objects
    if config is None:
        version = 'v0.1'
        app_name = 'pyPhyTrees'
        description = 'Phylogenetic Tree Construction and Visualization Tool'
    else:
        # Handle both dictionary and OmegaConf DictConfig formats
        try:
            # For OmegaConf DictConfig objects
            version = config.software.version
            app_name = config.software.app_name
            description = config.software.description
        except (AttributeError, KeyError):
            # For regular dictionaries
            software = config.get('software', {}) if hasattr(config, 'get') else config['software']
            version = software.get('version', 'v0.1') if hasattr(software, 'get') else software['version']
            app_name = software.get('app_name', 'pyPhyTrees') if hasattr(software, 'get') else software['app_name']
            description = software.get('description', 'Phylogenetic Tree Construction and Visualization Tool') if hasattr(software, 'get') else software['description']
    
    show_logo(
        "welcome",
        version=version,
        app_name=app_name,
        description=description,
        rice_color='bold cyan',
        use_gradient= True,
        gradient_colors=["red", "#ff9900", "#ff0", "Lime"]
    )

if __name__ == "__main__":
    # Create a test config dict to test the function
    Test_config = {
        'software': {
            'version': 'v0.0.1-test',
            'app_name': 'MyTestApp',
            'description': 'This is a test with gradient effect.',
        }
    }
    config2logo(config = Test_config)