"""Push data to dvc."""

import os
import re
import shutil
from pathlib import Path

from dvc.cli import main as dvc_main
from git import GitCommandError, Repo

from src import utils
from src.utils import logger


def dvc_remote_add(config):
    """Set the dvc remote."""
    access_key_id = os.getenv("DVC_ACCESS_KEY_ID")
    secret_access_key = os.getenv("DVC_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_DEFAULT_REGION")
    try:
        dvc_remote_name = os.getenv(
            "DVC_REMOTE_NAME", config["dvc_remote_name"]
        )
        dvc_remote = os.getenv("DVC_REMOTE", config["dvc_remote"])
        dvc_endpoint_url = os.getenv(
            "DVC_ENDPOINT_URL", config["dvc_endpoint_url"]
        )

        dvc_main(["remote", "add", "-f", dvc_remote_name, dvc_remote])
        dvc_main(
            [
                "remote",
                "modify",
                dvc_remote_name,
                "endpointurl",
                dvc_endpoint_url,
            ]
        )
        if secret_access_key is None:
            # Set dvc credentials only when a valid secret access key is set
            logger.warning(
                "AWS credentials `dvc_secret_access_key` is missing "
                "in the Airflow connection."
            )
        else:
            dvc_main(
                [
                    "remote",
                    "modify",
                    dvc_remote_name,
                    "access_key_id",
                    access_key_id,
                ]
            )
            dvc_main(
                [
                    "remote",
                    "modify",
                    dvc_remote_name,
                    "secret_access_key",
                    secret_access_key,
                ]
            )
        # Minio does not enforce regions but DVC requires it
        dvc_main(["remote", "modify", dvc_remote_name, "region", region])
    except Exception as e:
        logger.error(f"DVC remote add failed with error: {e}")
        raise e


def dvc_add_files(config):
    """Add train, test and val data files to DVC."""
    try:
        dvc_main(
            ["add", config["data_split"]["train_data_save_path"]],
        )
        dvc_main(
            ["add", config["data_split"]["test_data_save_path"]],
        )
        dvc_main(
            ["add", config["data_split"]["val_data_save_path"]],
        )
    except Exception as e:
        logger.error(f"DVC add failed with error: {e}")
        raise e


def dvc_push(config):
    """DVC push."""
    try:
        dvc_main(["push", "-r", config["dvc_remote_name"]])
    except Exception as e:
        logger.error(f"DVC push failed with error: {e}")
        raise e


def create_and_switch_branch(repo, config):
    """Create a branch if it doesn't exist and switch to it."""
    try:
        try:
            repo.git.checkout(config["git_branch"])
        except GitCommandError:
            # If branch does not exist, create it
            repo.git.checkout("HEAD", b=config["git_branch"])
    except Exception as e:
        logger.error(f"Git branch creation/switch failed with error: {e}")
        raise e


def add_suffix(file_name, suffix: str = ".dvc"):
    """Add an extra suffix to the filename."""
    return str(Path(file_name).with_suffix(Path(file_name).suffix + suffix))


def git_add_files(repo, config):
    """Git add required files."""
    try:
        repo.index.add(
            add_suffix(config["data_split"]["train_data_save_path"])
        )
        repo.index.add(add_suffix(config["data_split"]["val_data_save_path"]))
        repo.index.add(add_suffix(config["data_split"]["test_data_save_path"]))
        # Add the dvc config as well
        repo.index.add(".dvc/config")
    except Exception as e:
        logger.error(f"Git add failed with error: {e}")
        raise e


def git_commit(repo, config):
    """Git commit with message."""
    try:
        repo.index.commit(config["commit_message"])
    except Exception as e:
        logger.error(f"Git commit failed with error: {e}")
        raise e


def get_latest_tag(repo):
    """Get the latest tag and increment the minor version by 1."""
    try:
        # Get only the data tags
        tags = [
            tag
            for tag in repo.tags
            if re.match(r"data-v(\d+)\.(\d+)\.(\d+)", tag.name)
        ]
        # Sort the filtered data tags by commit date
        tags = sorted(tags, key=lambda t: t.commit.committed_datetime)
        if tags:
            latest_tag = tags[-1].name
            match = re.match(r"data-v(\d+)\.(\d+)\.(\d+)", latest_tag)
            if match:
                major, minor, patch = map(int, match.groups())
                new_tag = f"data-v{major}.{minor + 1}.{patch}"
                return new_tag
    except Exception as e:
        logger.error(f"Tag increment failed with error: {e}")
        raise e
    # if no tag, then tag it as data-1.0.0
    return "data-v1.0.0"


def git_push(repo, config):
    """Git push the commit and tag."""
    repo.git.push("origin", config["git_branch"])
    latest_tag = get_latest_tag(repo)
    repo.create_tag(latest_tag)
    repo.git.push("origin", latest_tag)


def copy_directory(src, dst):
    """Copy source directory to destination directory."""
    if not os.path.exists(dst):
        os.makedirs(dst)
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True)
        shutil.rmtree(src)
        logger.info(f"Directory copied from {src} to {dst} successfully.")
    except Exception as e:
        logger.error(f"Error copying directory: {e}")
        raise e


def get_authenticated_github_url(base_url):
    """From the base git http url, generate an authenticated url."""
    username = os.getenv("GITHUB_USERNAME")
    password = os.getenv("GITHUB_PASSWORD")

    if not username or not password:
        logger.error(
            "GITHUB_USERNAME or GITHUB_PASSWORD environment variables not set"
        )
        raise ValueError(
            "GITHUB_USERNAME or GITHUB_PASSWORD environment variables not set"
        )

    # Separate protocol and the rest of the URL
    protocol, rest_of_url = base_url.split("://")

    # Construct the new URL with credentials
    new_url = f"{protocol}://{username}:{password}@{rest_of_url}"

    return new_url


def checkout_branch(repo_dir, branch_name):
    """Git checkout."""
    repo = Repo(repo_dir)
    repo.git.fetch()

    # Check if the branch exists
    try:
        repo.git.rev_parse("--verify", f"refs/remotes/origin/{branch_name}")
        branch_exists = True
    except GitCommandError:
        branch_exists = False

    # Create the branch if it doesn't exist
    if branch_exists:
        repo.git.checkout(branch_name)
    else:
        repo.git.checkout("-b", branch_name)

    return branch_exists


def pull_updates(repo_dir):
    """Git pull."""
    Repo(repo_dir).remotes.origin.pull()


def push_data(config):
    """Push the data and tag it with version."""
    # 1. Authenticate, clone, and update git repo
    authenticated_git_url = get_authenticated_github_url(
        config["git_repo_url"]
    )
    repo_temp_path = "./repo"
    Repo.clone_from(authenticated_git_url, repo_temp_path)
    branch_exists = checkout_branch(repo_temp_path, config["git_branch"])
    if branch_exists:
        pull_updates(repo_temp_path)

    copy_directory(repo_temp_path, config["git_repo_save_name"])
    os.chdir(config["git_repo_save_name"])

    # 2. Initialise git and dvc
    repo = Repo("./")
    assert not repo.bare

    # TODO: ensure we have proper dvc remote
    # dvc_main(
    #     ["init"],
    # )

    # 3. DVC operations
    logger.warning("STARTING DVC REMOTE ADD")
    dvc_remote_add(config)
    logger.warning("STARTING DVC ADD")
    dvc_add_files(config)
    logger.warning("STARTING DVC PUSH")
    dvc_push(config)
    logger.warning("ENDED DVC PUSH")

    # 4. Git operations:
    # Create a branch if it doesn't exist and switch to it
    create_and_switch_branch(repo, config)

    # Git add some files
    git_add_files(repo, config)

    # Git commit the changes
    git_commit(repo, config)

    # Git push the commit and tag/version
    git_push(repo, config)


if __name__ == "__main__":
    config = utils.load_yaml_config()
    push_data(config)
