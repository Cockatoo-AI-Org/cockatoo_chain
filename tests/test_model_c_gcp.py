from cockatoo_chain.utils.model_c import gcp
from cockatoo_chain.utils import wrapper
import unittest
from unittest.mock import mock_open, patch


LangEnum = wrapper.LangEnum


class TestCockatooChain(unittest.TestCase):
  """Test class for `model_c.gcp` module."""

  def setUp(self):
    """Setup phase."""
    self.tts_patcher = patch('cockatoo_chain.utils.model_c.gcp.tts')
    self.mock_tts = self.tts_patcher.start()
    self.service_account_patcher = patch(
        'cockatoo_chain.utils.model_c.gcp.service_account')
    self.mock_service_account = self.service_account_patcher.start()
    self.mock_gcp_client = self.mock_tts.TextToSpeechClient.return_value
    self.test_settings = {'lang': LangEnum.en}
    self.gcp_wrapper = gcp.GCPText2SpeechWrapper(self.test_settings)

  def test_gcp_wrapper_attributes(self):
    """Test case."""
    self.assertEqual(self.gcp_wrapper.lang, LangEnum.en)
    self.assertEqual(self.gcp_wrapper.client, self.mock_gcp_client)
    self.assertEqual(self.gcp_wrapper.name, 'GCP/text-to-speech')

  @patch("builtins.open", new_callable=mock_open)
  @patch('cockatoo_chain.utils.model_c.gcp.time')
  def test_gcp_wrapper_text_2_audio(self, mock_time, mock_file):
    """Test case."""
    test_text = 'helloworld'
    mock_time.time.side_effect = [0, 1]

    response = self.gcp_wrapper.text_2_audio(test_text)

    self.assertEqual(response.text, test_text)
    self.assertEqual(response.spent_time_sec, 1)
    self.assertEqual(response.generated_audio_file_path, gcp.AUDIO_OUTPUT_PATH)

  def tearDown(self):
    """Stop the patch after each test."""
    self.tts_patcher.stop()
    self.service_account_patcher.stop()
