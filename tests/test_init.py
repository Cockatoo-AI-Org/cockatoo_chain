import cockatoo_chain
import os
from unittest.mock import patch
import pytest


class TestCockatooChain:
  """Test class for simple add function as template example."""

  @pytest.mark.parametrize(
      'env_path', (None, '~/.test'))
  @patch('cockatoo_chain.find_dotenv')
  @patch('cockatoo_chain.load_dotenv')
  def test_load_env(self, mock_load_dotenv, mock_find_dotenv, env_path):
    """Test function `load_env`."""
    expanded_env_path = (
        os.path.expanduser(env_path) if env_path else
        os.path.expanduser('~/.env'))
    find_dotenv_output = mock_find_dotenv.return_value

    cockatoo_chain.load_env(env_path)

    mock_find_dotenv.assert_called_with(expanded_env_path)
    mock_load_dotenv.assert_called_with(find_dotenv_output)
