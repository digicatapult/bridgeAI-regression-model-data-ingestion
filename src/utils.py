"""Utility functions."""

import logging
import os
import subprocess
import sys

import yaml
from pythonjsonlogger import jsonlogger


def load_yaml_config(config_path: str = "./config.yaml"):
    """Load the json configuration."""
    config_path = os.getenv("CONFIG_PATH", config_path)
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    return config


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom log formatter."""

    def add_fields(self, log_record, record, message_dict):
        """Adding standard filed for logging."""
        super(CustomJsonFormatter, self).add_fields(
            log_record, record, message_dict
        )
        log_record["module"] = record.module
        log_record["funcName"] = record.funcName
        log_record["pathname"] = record.pathname
        log_record["lineno"] = record.lineno
        log_record["filename"] = record.filename
        log_record["levelname"] = record.levelname


def setup_logger():
    logger = logging.getLogger()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # set the logging level to info if the provided one is invalid
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Create a stream handler to log to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter("%(asctime)s %(message)s")
    stream_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(stream_handler)

    return logger


def add_to_dvc(config):
    """Add a file to DVC and git."""
    try:
        # Set the dvc remote if not already set
        subprocess.run(
            [
                "dvc",
                "remote",
                "add",
                "-f",
                config["dvc_remote_name"],
                config["dvc_remote"],
            ],
            check=True,
        )
        # Add files to DVC
        subprocess.run(
            ["dvc", "add", config["data_split"]["train_data_save_path"]],
            check=True,
        )
        subprocess.run(
            ["dvc", "add", config["data_split"]["test_data_save_path"]],
            check=True,
        )
        subprocess.run(
            ["dvc", "add", config["data_split"]["val_data_save_path"]],
            check=True,
        )

        # dvc push
        subprocess.run(
            ["dvc", "push", "-r", config["dvc_remote_name"]],
            check=True,
        )

        print("Added files to DVC.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add to DVC. Error: {e}")


def switch_or_create_branch(branch_name):
    try:
        # Try to switch to the branch
        subprocess.run(["git", "checkout", branch_name], check=True)
        print(f"Switched to branch: {branch_name}")
    except subprocess.CalledProcessError:
        try:
            # If the branch does not exist, create and switch to it
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            print(f"Created and switched to branch: {branch_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create branch: {branch_name}. Error: {e}")


def commit_to_git(config, commit_message="add data to dvc"):
    """Commit DVC files to Git."""
    switch_or_create_branch(config["git_branch"])
    try:
        # Add the .dvc file to git
        subprocess.run(
            [
                "git",
                "add",
                f"{config['data_split']['train_data_save_path']}.dvc",
            ],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "add",
                f'{config["data_split"]["test_data_save_path"]}.dvc',
            ],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "add",
                f'{config["data_split"]["val_data_save_path"]}.dvc',
            ],
            check=True,
        )
        subprocess.run(["git", "add", ".dvcignore", ".gitignore"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"{commit_message}"], check=True
        )
        subprocess.run(
            ["git", "push", "origin", config["git_branch"]], check=True
        )

        print("Changes committed and pushed to Git.")
    except Exception as e:
        print(f"Failed to commit changes to Git. Error: {e}")


# Initialized logger
logger = setup_logger()
