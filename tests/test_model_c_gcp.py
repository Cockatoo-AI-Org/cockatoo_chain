from cockatoo_chain.utils.model_c import gcp
from cockatoo_chain.utils import wrapper
import unittest
from unittest.mock import mock_open, patch, MagicMock


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
    # Mock the environment variable for credentials
    self.os_environ_patcher = patch(
        'os.environ.get', return_value='/tmp/mock_creds.json')
    self.mock_os_environ = self.os_environ_patcher.start()

    self.mock_gcp_client = self.mock_tts.TextToSpeechClient.return_value
    self.test_settings = {'lang': LangEnum.en}
    self.gcp_wrapper = gcp.GCPText2SpeechWrapper(self.test_settings)

  def tearDown(self):
    """Stop the patch after each test."""
    self.tts_patcher.stop()
    self.service_account_patcher.stop()
    self.os_environ_patcher.stop()

  def test_gcp_wrapper_attributes(self):
    """Test `GCPText2SpeechWrapper` initialization and properties."""
    self.assertEqual(self.gcp_wrapper.lang, LangEnum.en)
    self.assertEqual(self.gcp_wrapper.client, self.mock_gcp_client)
    self.assertEqual(self.gcp_wrapper.name, 'GCP/text-to-speech')
    # Verify that os.environ.get was called for GOOGLE_APPLICATION_CREDENTIALS
    self.mock_os_environ.assert_called_with('GOOGLE_APPLICATION_CREDENTIALS')
    mock_cred = self.mock_service_account.Credentials
    mock_cred.from_service_account_file.assert_called_once_with(
        '/tmp/mock_creds.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

  @patch("builtins.open", new_callable=mock_open)
  @patch('cockatoo_chain.utils.model_c.gcp.time')
  def test_gcp_wrapper_text_2_audio(self, mock_time, mock_file):
    """Test `text_2_audio` method with default output path."""
    test_text = 'helloworld'
    mock_time.time.side_effect = [0, 1]
    mock_response = MagicMock()
    mock_response.audio_content = b'mock_audio_content'
    self.mock_gcp_client.synthesize_speech.return_value = mock_response
    mock_synthesis_input = self.mock_tts.SynthesisInput.return_value
    mock_voice_params = self.mock_tts.VoiceSelectionParams.return_value
    mock_audio_config = self.mock_tts.AudioConfig.return_value

    response = self.gcp_wrapper.text_2_audio(test_text)

    # Assert GCP client's synthesize_speech was called correctly
    self.mock_gcp_client.synthesize_speech.assert_called_once()
    print(f'Test: {self.mock_gcp_client.synthesize_speech.call_args[1]}')
    call_args = self.mock_gcp_client.synthesize_speech.call_args
    self.assertEqual(call_args[1]['input'], mock_synthesis_input)
    self.assertEqual(call_args[1]['voice'], mock_voice_params)
    self.assertEqual(call_args[1]['audio_config'], mock_audio_config)

    # Assert file was opened and written to
    mock_file.assert_called_once_with(gcp.AUDIO_OUTPUT_PATH, 'wb')
    mock_file().write.assert_called_once_with(b'mock_audio_content')

    self.assertEqual(response.text, test_text)
    self.assertEqual(response.spent_time_sec, 1)
    self.assertEqual(response.generated_audio_file_path, gcp.AUDIO_OUTPUT_PATH)

  @patch("builtins.open", new_callable=mock_open)
  @patch('cockatoo_chain.utils.model_c.gcp.time')
  def test_gcp_wrapper_text_2_audio_custom_path(self, mock_time, mock_file):
    """Test `text_2_audio` method with a custom output path."""
    test_text = 'hello custom'
    custom_path = '/tmp/custom_output.wav'
    mock_time.time.side_effect = [0, 1]
    mock_response = MagicMock()
    mock_response.audio_content = b'mock_audio_content_custom'
    self.mock_gcp_client.synthesize_speech.return_value = mock_response

    response = self.gcp_wrapper.text_2_audio(test_text, custom_path)

    self.mock_gcp_client.synthesize_speech.assert_called_once()
    mock_file.assert_called_once_with(custom_path, 'wb')
    mock_file().write.assert_called_once_with(b'mock_audio_content_custom')

    self.assertEqual(response.text, test_text)
    self.assertEqual(response.spent_time_sec, 1)
    self.assertEqual(response.generated_audio_file_path, custom_path)

  def test_gcp_wrapper_get_supported_languages(self):
    """Test `get_supported_languages` method."""
    mock_voice1 = MagicMock()
    mock_voice1.language_codes = ['en-US', 'en-GB']
    mock_voice2 = MagicMock()
    mock_voice2.language_codes = ['fr-FR']
    mock_response = MagicMock()
    mock_response.voices = [mock_voice1, mock_voice2]
    self.mock_gcp_client.list_voices.return_value = mock_response

    supported_languages = self.gcp_wrapper.get_supported_languages()

    # No arguments expected for list_voices() in this context
    self.mock_gcp_client.list_voices.assert_called_once_with()
    self.assertEqual(supported_languages, {'en-US', 'en-GB', 'fr-FR'})

  @patch('builtins.print')
  def test_gcp_wrapper_list_voices(self, mock_print):
    """Test `list_voices` method with a language code."""
    mock_gender1 = MagicMock()
    mock_gender2 = MagicMock()
    self.mock_tts.SsmlVoiceGender.side_effect = [mock_gender1, mock_gender2]
    # Create mock voice objects mirroring expected structure
    mock_voice1 = MagicMock()
    mock_voice1.language_codes = ['en-US']
    mock_voice1.name = 'en-US-Standard-A'
    mock_voice1.ssml_gender = mock_gender1
    mock_voice1.ssml_gender.name = 'FEMALE'
    mock_voice1.natural_sample_rate_hertz = 24000

    mock_voice2 = MagicMock()
    mock_voice2.language_codes = ['fr-FR']
    mock_voice2.name = 'fr-FR-Wavenet-B'
    mock_voice2.ssml_gender = mock_gender2
    mock_voice2.ssml_gender.name = 'MALE'
    mock_voice2.natural_sample_rate_hertz = 16000

    mock_response = MagicMock()
    # Ensure voices are sorted as they would be in the actual method
    mock_response.voices = sorted(
        [mock_voice1, mock_voice2], key=lambda voice: voice.name)
    self.mock_gcp_client.list_voices.return_value = mock_response

    self.gcp_wrapper.list_voices('en-US')

    # Assert that the client's list_voices was called with the correct argument
    self.mock_gcp_client.list_voices.assert_called_once_with(
        language_code='en-US')
    # Assert specific print calls. Order and content are important here.
    mock_print.assert_any_call(' Voices: 2 '.center(60, "-"))
    mock_print.assert_any_call(
        'en-US    | en-US-Standard-A         | FEMALE   | 24,000 Hz')
    mock_print.assert_any_call(
        'fr-FR    | fr-FR-Wavenet-B          | MALE     | 16,000 Hz')

  @patch('cockatoo_chain.utils.model_c.base.logging')
  @patch.object(gcp.GCPText2SpeechWrapper, 'text_2_audio')
  def test_speak_text(self, mock_text_2_audio, mock_logging):
    """Test `speak_text` method, which calls `text_2_audio` and logs."""
    test_text = 'This is a test speech.'
    # Mock the return value of text_2_audio
    mock_audio_data = wrapper.Text2AudioData(
        text=test_text,
        spent_time_sec=0.5,
        generated_audio_file_path='/tmp/test_speech_audio.wav'
    )
    mock_text_2_audio.return_value = mock_audio_data

    self.gcp_wrapper.speak_text(test_text)

    # Assert that text_2_audio was called with the correct text
    mock_text_2_audio.assert_called_once_with(test_text)
    # Assert that logging.info was called with the correct message and path
    mock_logging.info.assert_called_once_with(
        'Play audio from %s', mock_audio_data.generated_audio_file_path)
