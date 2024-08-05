"""Unit test for data push."""

from unittest.mock import MagicMock, patch

from src.data_push import push_data


@patch("src.data_push.get_authenticated_github_url")
@patch("src.data_push.Repo")
@patch("src.data_push.checkout_branch")
@patch("src.data_push.pull_updates")
@patch("src.data_push.copy_directory")
@patch("src.data_push.dvc_main")
@patch("src.data_push.dvc_remote_add")
@patch("src.data_push.dvc_add_files")
@patch("src.data_push.dvc_push")
@patch("src.data_push.create_and_switch_branch")
@patch("src.data_push.git_add_files")
@patch("src.data_push.git_commit")
@patch("src.data_push.git_push")
@patch("src.data_push.os")
def test_push_data(
    mock_os,
    mock_git_push,
    mock_git_commit,
    mock_git_add_files,
    mock_create_and_switch_branch,
    mock_dvc_push,
    mock_dvc_add_files,
    mock_dvc_remote_add,
    mock_dvc_main,
    mock_copy_directory,
    mock_pull_updates,
    mock_checkout_branch,
    mock_Repo,
    mock_get_authenticated_github_url,
):
    mock_os.return_value = MagicMock()
    # Mocking the return values
    mock_get_authenticated_github_url.return_value = (
        "https://authenticated-url"
    )
    mock_repo = MagicMock()
    mock_repo.bare = False
    mock_Repo.return_value = mock_repo

    config = {
        "git_repo_url": "https://example.com/repo.git",
        "git_branch": "main",
        "git_repo_save_name": "repo_dir",
        # Additional config for dvc
    }

    # Call the function
    push_data(config)

    # Assertions
    mock_get_authenticated_github_url.assert_called_once_with(
        config["git_repo_url"]
    )
    mock_dvc_remote_add.assert_called_once_with(config)
    mock_dvc_add_files.assert_called_once_with(config)
    mock_dvc_push.assert_called_once_with(config)
    mock_create_and_switch_branch.assert_called_once_with(mock_repo, config)
    mock_git_add_files.assert_called_once_with(mock_repo, config)
    mock_git_commit.assert_called_once_with(mock_repo, config)
    mock_git_push.assert_called_once_with(mock_repo, config)
