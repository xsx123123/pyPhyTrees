#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import datetime
import os
from loguru import logger
from omegaconf import DictConfig
from hydra.core.hydra_config import HydraConfig
# ------ logger initialization ------ #
def logger_init(logger_name:str,cfg:DictConfig):
    """
    配置并返回一个 Loguru 日志记录器实例。
    这个函数设置了日志的格式、颜色和输出位置。
    """
    logger.remove()
    if cfg.logs.more_info:
        logger.add(sys.stdout,format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> |"
                "{level.icon}|"
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>",
                level=cfg.logs.log_level,colorize=True,serialize=False)
        logger.add(logger_name,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> |"
                "{level.icon}|"
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>",
                level=cfg.logs.log_level,colorize=True,serialize=False)
    else:
        logger.add(sys.stdout,format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level}</level> | <level>{message}</level>",
                level=cfg.logs.log_level,colorize=True,serialize=False)
        logger.add(logger_name,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level}</level> | <level>{message}</level>",
                level=cfg.logs.log_level,colorize=True,serialize=False)
    return logger
 
def logger_generator(cfg:DictConfig, output_dir=None): 
    """
    配置并返回一个 Loguru 日志记录器实例。
    这个函数设置了日志的格式、颜色和输出位置。
    """ 
    times = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    # Try to get Hydra output directory, but provide fallback if not running in Hydra
    try:
        hydra_output_dir = HydraConfig.get().runtime.output_dir
        logger_name = f"{hydra_output_dir}/{cfg.logs.project_id}_{times}.log"
        actual_output_dir = hydra_output_dir
    except (ValueError, AttributeError):
        # Fallback when not running within Hydra
        if output_dir:
            actual_output_dir = output_dir
        else:
            actual_output_dir = os.getcwd()  # Use current directory as fallback
        logger_name = f"{actual_output_dir}/{cfg.logs.project_id if hasattr(cfg, 'logs') and hasattr(cfg.logs, 'project_id') else 'pyPhyTrees'}_{times}.log"
    
    # Remove the default logger to avoid duplicate logs
    logger_instance = logger_init(logger_name if os.path.dirname(logger_name) != '' else None, cfg)
    
    # Log additional information if they exist in the config (for older config formats)
    if hasattr(cfg, 'RecombTracer'):
        if hasattr(cfg.RecombTracer, 'Author'):
            logger_instance.info(f"RecombTracer Author:{cfg.RecombTracer.Author}")
        if hasattr(cfg.RecombTracer, 'Version'):
            logger_instance.info(f"RecombTracer Version:{cfg.RecombTracer.Version}")
        if hasattr(cfg.RecombTracer, 'Email'):
            logger_instance.info(f"RecombTracer Email:{cfg.RecombTracer.Email}")
    
    logger_instance.info(f"Logger initialized, log file: {logger_name}")
    logger_instance.info(f"Analysis workspace: {os.getcwd()}")
    logger_instance.info(f"Analysis Result directory: {actual_output_dir}")
    logger_instance.debug(f"Full config: {cfg}")
    
    return logger_instance, actual_output_dir
# ------ logger initialization ------ #