from cockatoo_chain.utils.model_a import open_ai
from cockatoo_chain.utils import wrapper
import os
import tempfile
import unittest
from unittest.mock import patch


LangEnum = wrapper.LangEnum


class TestCockatooChain(unittest.TestCase):
  """Test class for `model_a.open_ai` module."""

  def setUp(self):
    """Setup phase."""
    self.patcher = patch('cockatoo_chain.utils.model_a.open_ai.openai')
    self.mock_open_ai = self.patcher.start()

  def test_open_ai_wrapper_attributes(self):
    """Test function `load_env`."""
    settings = {'lang': LangEnum.en}
    mock_open_ai_client = self.mock_open_ai.OpenAI.return_value

    open_ai_wrapper = open_ai.OpenAIWrapper(settings)

    self.assertEqual(open_ai_wrapper.lang, settings['lang'])
    self.assertEqual(open_ai_wrapper.client, mock_open_ai_client)
    self.assertEqual(open_ai_wrapper.name, 'OpenAI/speech-to-text')

  @patch('cockatoo_chain.utils.model_a.open_ai.time')
  def test_open_ai_wrapper_audio_2_text(self, mock_time):
    """Test method `wrapper.audio_2_text(...)`."""
    mock_time.time.side_effect = [0, 1]
    mock_open_ai_client = self.mock_open_ai.OpenAI.return_value
    mock_transcription = (
      mock_open_ai_client.audio.transcriptions.create.return_value)
    mock_transcription.text = 'helloworld'
    settings = {'lang': LangEnum.cn}

    with tempfile.TemporaryDirectory() as temp_dir:
      # mock reading audio file
      test_file_path = os.path.join(temp_dir, 'test_audio.wav')
      with open(test_file_path, 'wb') as f:
        f.write('fake audio content'.encode('utf-8'))
      open_ai_wrapper = open_ai.OpenAIWrapper(settings)
      response = open_ai_wrapper.audio_2_text(test_file_path)

      self.assertEqual(open_ai_wrapper.lang, settings['lang'])
      self.assertEqual(response.text, 'helloworld')
      self.assertEqual(response.spent_time_sec, 1)
      self.assertEqual(response.audio_file_path, test_file_path)

  @patch('cockatoo_chain.utils.model_a.open_ai.time')
  def test_open_ai_wrapper_audio_2_text_with_exception(
      self, mock_time):
    """Test method `wrapper.audio_2_text(...)` with exception."""
    mock_open_ai_client = self.mock_open_ai.OpenAI.return_value
    mock_open_ai_client.audio.transcriptions.create.side_effect = (
        Exception('test'))
    open_ai_wrapper = open_ai.OpenAIWrapper({'lang': LangEnum.cn})
    with tempfile.NamedTemporaryFile(mode="w+") as temp_file:
      with self.assertRaises(Exception):
        open_ai_wrapper.audio_2_text(temp_file.name)

  def test_open_ai_wrapper_live_2_text(self):
    """Test method `wrapper.live_2_text(...)`."""
    settings = {'lang': LangEnum.cn}
    test_record_time_sec = 1
    test_output_audio_file_path = 'test_output_audio_file_path'
    open_ai_wrapper = open_ai.OpenAIWrapper(settings)

    with self.assertRaises(NotImplementedError):
      open_ai_wrapper.live_2_text(
          test_record_time_sec,
          test_output_audio_file_path)

  def tearDown(self):
    """Stop the patch after each test."""
    self.patcher.stop()
