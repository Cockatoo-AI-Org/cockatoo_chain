from cockatoo_chain.utils.model_a import gcp
from cockatoo_chain.utils import wrapper
import os
import tempfile
import unittest
from unittest import mock
from unittest.mock import patch


LangEnum = wrapper.LangEnum


class TestCockatooChain(unittest.TestCase):
  """Test class for `model_a.gcp` module."""

  def setUp(self):
    """Setup phase."""
    self.stt_patcher = patch('cockatoo_chain.utils.model_a.gcp.stt')
    self.service_account_patcher = patch(
        'cockatoo_chain.utils.model_a.gcp.service_account')
    self.mock_stt = self.stt_patcher.start()
    self.mock_service_account = self.service_account_patcher.start()
    self.mock_gcp_client = self.mock_stt.SpeechClient.return_value
    self.test_settings = {'lang': LangEnum.en}
    self.gcp_wrapper = gcp.GCPSpeech2TextWrapper(self.test_settings)

  def test_gcp_wrapper_attributes(self):
    """Test case."""
    self.assertEqual(self.gcp_wrapper.lang, LangEnum.en)
    self.assertEqual(self.gcp_wrapper.client, self.mock_gcp_client)
    self.assertEqual(self.gcp_wrapper.name, 'GCP/speech-to-text')

  @patch('cockatoo_chain.utils.model_a.gcp.time')
  def test_gcp_wrapper_audio_2_text(self, mock_time):
    """Test case."""
    mock_response = self.mock_gcp_client.recognize.return_value
    mock_result = mock.MagicMock()
    mock_alternative = mock.MagicMock()
    mock_alternative.transcript = 'helloworld'
    mock_result.alternatives = [mock_alternative]
    mock_response.results = [mock_result]
    mock_time.time.side_effect = [0, 1]
    self.gcp_wrapper._frame_rate_channel = mock.MagicMock(
      return_value=(1, 2))

    with tempfile.TemporaryDirectory() as temp_dir:
      # mock reading audio file
      test_file_path = os.path.join(temp_dir, 'test_audio.wav')
      with open(test_file_path, 'wb') as f:
        f.write('fake audio content'.encode('utf-8'))
      response = self.gcp_wrapper.audio_2_text(test_file_path)

      self.assertEqual(response.text, 'helloworld')
      self.assertEqual(response.spent_time_sec, 1)
      self.assertEqual(response.audio_file_path, test_file_path)

  def tearDown(self):
    """Stop the patch after each test."""
    self.stt_patcher.stop()
    self.service_account_patcher.stop()
