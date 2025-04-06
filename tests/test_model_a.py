from cockatoo_chain.utils import model_a
from cockatoo_chain.utils import wrapper
import unittest
from unittest.mock import patch


LangEnum = wrapper.LangEnum
ModelType = model_a.ModelType


class TestCockatooChain(unittest.TestCase):
  """Test class for simple add function as template example."""

  @patch('cockatoo_chain.utils.model_a.open_ai')
  def test_get_open_ai_whisper(self, mock_open_ai):
    """Test function `load_env`."""
    mock_open_ai_whisper = mock_open_ai.OpenAIWrapper.return_value

    return_value = model_a.get(ModelType.OPEN_AI_WHISPER)

    mock_open_ai.OpenAIWrapper.assert_called_with(
       {'lang': LangEnum.en})
    self.assertEqual(return_value, mock_open_ai_whisper)

  def test_get_invalid_model_type(self):
    """Test model_a.get(...) with invalid type."""
    with self.assertRaises(ValueError):
      model_a.get('Invalid model type')
