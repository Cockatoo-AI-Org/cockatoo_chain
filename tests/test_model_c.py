from cockatoo_chain.utils import model_c
from cockatoo_chain.utils import wrapper
import unittest
from unittest.mock import patch


LangEnum = wrapper.LangEnum
ModelType = model_c.ModelType


class TestCockatooChain(unittest.TestCase):
  """Test class for simple add function as template example."""

  @patch('cockatoo_chain.utils.model_c.gcp')
  def test_get_open_ai_whisper(self, mock_gcp):
    """Test case."""
    mock_gcp_model_wrapper = mock_gcp.GCPText2SpeechWrapper.return_value

    return_value = model_c.get(ModelType.GCP_TEXT_2_SPEECH)

    mock_gcp.GCPText2SpeechWrapper.assert_called_with(
       {'lang': LangEnum.en})
    self.assertEqual(return_value, mock_gcp_model_wrapper)

  def test_get_invalid_model_type(self):
    """Test model_a.get(...) with invalid type."""
    with self.assertRaises(ValueError):
      model_c.get('Invalid model type')
