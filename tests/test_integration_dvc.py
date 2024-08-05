import os
import subprocess

import pytest


@pytest.fixture
def setup_and_teardown():
    """Set up the required files and clean up after."""
    repo_path = "./test_dvc_repo"
    os.makedirs(repo_path, exist_ok=True)
    os.chdir(repo_path)
    subprocess.run(["git", "init"])
    os.makedirs("./artefacts", exist_ok=True)
    os.chdir("../")
    yield repo_path
    subprocess.run(["rm", "-rf", repo_path], check=True)
    subprocess.run(["rm", "data.txt"], check=True)
    subprocess.run(["rm", "data.txt.dvc"], check=True)


def test_push_data_dvc(setup_and_teardown):
    config = {
        # TODO: change this remote to an s3
        "dvc_remote": "./artefacts",
        "dvc_remote_name": "regression-model-remote",
    }

    # Add a file to DVC
    with open("data.txt", "w") as f:
        f.write("data")
    subprocess.run(["dvc", "add", "data.txt"], check=True)
    # setup a local remote
    dvc_add_result = subprocess.run(
        [
            "dvc",
            "remote",
            "add",
            "-f",
            config["dvc_remote_name"],
            config["dvc_remote"],
        ]
    )
    # test a dvc push to remote
    dvc_push_result = subprocess.run(
        ["dvc", "push", "-r", config["dvc_remote_name"]], check=True
    )

    assert dvc_add_result.returncode == 0
    assert dvc_push_result.returncode == 0
