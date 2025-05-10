"""Wrapper of GCP STT solution."""
import logging
import os
import time
import wave
from google.cloud import speech as stt
# from google.cloud import speech_v2 as stt
from google.oauth2 import service_account

from cockatoo_chain.utils import wrapper
from cockatoo_chain.utils.model_a import base


AUDIO_INPUT_PATH = '/tmp/gcp_stt_input.wav'
Audio2TextData = wrapper.Audio2TextData
ModelBase = base.ModelBase


class GCPSpeech2TextWrapper(ModelBase):
  """Wrapper of GCP Speech to text API v1.

  For details of this wrapper, please refer to below doc:
  - https://cloud.google.com/speech-to-text?hl=en  # noqa: E501

  For this class to work correctly, we have to provide below environment
  variable(s):
  - GOOGLE_APPLICATION_CREDENTIALS: GCP credentials file path.

  Also, you need to enable text to speech API from your GCP project:
  - https://cloud.google.com/speech-to-text/docs/before-you-begin

  For `settings`, we support:
  - audio_input_path: Path of audio file to do the transformation. (Optional)
  - language_code: Language code. e.g. "en-US" as default. (Optional) For the
    supported language code, refer to:
    https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
  """
  def __init__(self, settings):
    super().__init__(settings['lang'])
    key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    self._credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=[
            'https://www.googleapis.com/auth/cloud-platform'])
    logging.info('Start authorizing...')
    self._client = stt.SpeechClient()
    self._input_path = settings.get('audio_input_path', AUDIO_INPUT_PATH)
    self._language_code = settings.get('language_code', 'en-US')

  @property
  def client(self) -> stt.SpeechClient:
    """Gets client of GCP STT solution."""
    return self._client

  @property
  def name(self) -> str:
    """Gets name of the wrapper."""
    return 'GCP/speech-to-text'

  def _frame_rate_channel(self, audio_file_path: str):
    with wave.open(audio_file_path, 'rb') as wave_file:
      frame_rate = wave_file.getframerate()
      channels = wave_file.getnchannels()
      return frame_rate, channels

  def audio_2_text(self, audio_file_path: str | None = None) -> Audio2TextData:
    """Turns audio from input audio file into text."""
    audio_file_path = audio_file_path or self._input_path
    audio_file_path = os.path.expanduser(audio_file_path)
    start_time = time.time()
    try:
      _, channels = self._frame_rate_channel(audio_file_path)
      with open(audio_file_path, 'rb') as f:
        audio_content = f.read()
        audio = stt.RecognitionAudio(content=audio_content)

      config = stt.RecognitionConfig(
          encoding=stt.RecognitionConfig.AudioEncoding.LINEAR16,
          enable_automatic_punctuation=True,
          audio_channel_count=channels,
          language_code=self._language_code)

      response = self.client.recognize(config=config, audio=audio)

      # Reads the response
      audio_text_list = []
      for result in response.results:
        audio_text_list.append(result.alternatives[0].transcript)

      audio_text = ''.join(audio_text_list)
      time_diff_sec = time.time() - start_time
      return Audio2TextData(
          text=audio_text,
          spent_time_sec=time_diff_sec,
          audio_file_path=audio_file_path)
    except Exception as ex:
      logging.error(
          f'Failed to transform audio to text from {audio_file_path}')
      raise ex
