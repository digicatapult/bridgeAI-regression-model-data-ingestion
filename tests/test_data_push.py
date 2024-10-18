"""Unit test for data push."""

from unittest.mock import MagicMock, patch

from src.data_push import get_latest_tag, push_data


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


def test_no_tags():
    """Test when there are no tags in the repository."""
    repo = MagicMock()
    repo.tags = []
    result = get_latest_tag(repo)
    assert result == "data-v1.0.0"


def test_valid_data_v_tag():
    """Test when a valid data-v tag exists.

    The version should be incremented.
    """
    repo = MagicMock()

    # Create a mock tag object
    tag = MagicMock()
    tag.name = "data-v1.2.0"
    tag.commit.committed_datetime = "2000-01-01"

    # Mock repo.tags to return the mock tag
    repo.tags = [tag]

    result = get_latest_tag(repo)
    assert result == "data-v1.3.0"


def test_multiple_data_v_tags():
    """Test when multiple valid data-v tags exist.

    The latest one should be selected and incremented.
    """
    repo = MagicMock()

    # Create multiple mock tag objects
    tag1 = MagicMock()
    tag1.name = "data-v1.1.0"
    tag1.commit.committed_datetime = "2000-01-01"

    tag2 = MagicMock()
    tag2.name = "data-v1.2.0"
    tag2.commit.committed_datetime = "2001-01-01"

    # Mock repo.tags to return both tags
    repo.tags = [tag1, tag2]

    result = get_latest_tag(repo)
    assert result == "data-v1.3.0"


def test_non_data_v_tags():
    """Test when non data-v tags exist.

    All the non data-v tags should be ignored."""
    repo = MagicMock()

    # Create mock tag objects where one is unrelated
    tag1 = MagicMock()
    tag1.name = "v1.0.1"
    tag1.commit.committed_datetime = "2002-01-01"

    tag2 = MagicMock()
    tag2.name = "data-v1.0.0"
    tag2.commit.committed_datetime = "2001-01-01"

    # Mock repo.tags to return both tags
    repo.tags = [tag1, tag2]

    result = get_latest_tag(repo)
    assert result == "data-v1.1.0"


def test_empty_data_v_tag():
    """Test when no valid data-v tag exists.

    Should return data-v1.0.0."""
    repo = MagicMock()

    # Mock repo.tags with tags that don't match the 'data-v' pattern
    tag1 = MagicMock()
    tag1.name = "v1.0.0"
    tag1.commit.committed_datetime = "2000-01-01"

    tag2 = MagicMock()
    tag2.name = "v2.0.0"
    tag2.commit.committed_datetime = "2001-01-01"

    repo.tags = [tag1, tag2]

    result = get_latest_tag(repo)
    assert result == "data-v1.0.0"
