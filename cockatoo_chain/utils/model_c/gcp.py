"""Integration of text to speech solution from GCP."""

import time
import logging
import os
from typing import Sequence
import google.cloud.texttospeech as tts
from google.oauth2 import service_account

from cockatoo_chain.utils import wrapper
from cockatoo_chain.utils.model_c import base


AUDIO_OUTPUT_PATH = '/tmp/gcp_tts_output.wav'
Text2AudioData = wrapper.Text2AudioData
ModelBase = base.ModelBase


class GCPText2SpeechWrapper(ModelBase):
  """Wrapper of GCP text to speech API.

  For details of this wrapper, please refer to below doc:
  - https://cloud.google.com/speech-to-text/docs/samples?hl=en  # noqa: E501

  For this class to work correctly, we have to provide below environment
  variable(s):
  - GOOGLE_APPLICATION_CREDENTIALS: GCP credentials file path.

  Also, you need to enable text to speech API from your GCP project:
  - https://cloud.google.com/text-to-speech/docs/before-you-begin

  For `settings`, we support:
  - audio_output_path: Path to save the transformed audio file.
  - voice_name: The voice name for transformation. e.g. `en-AU-Chirp-HD-D`.
  """

  def __init__(self, settings):
    super().__init__(settings.get('lang'))
    key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    self._output_path = settings.get('audio_output_path', AUDIO_OUTPUT_PATH)
    self._voice_name = settings.get('voice_name', 'en-US-Studio-O')
    self._credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=[
            'https://www.googleapis.com/auth/cloud-platform'])
    logging.info('Start authorizing...')
    self._client = tts.TextToSpeechClient()

  @property
  def client(self) -> tts.TextToSpeechClient:
    """Gets client of GCP TTS solution."""
    return self._client

  @property
  def name(self) -> str:
    """Gets name of the wrapper."""
    return 'GCP/text-to-speech'

  def _unique_languages_from_voices(
      self, voices: Sequence[tts.Voice]) -> set[str]:
    language_set = set()
    for voice in voices:
      for language_code in voice.language_codes:
        language_set.add(language_code)
    return language_set

  def get_supported_languages(self) -> set[str]:
    """Gets the supported languages."""
    response = self.client.list_voices()
    return self._unique_languages_from_voices(response.voices)

  def list_voices(self, language_code=None):
    """List supported voices of input language code."""
    response = self.client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)

    print(f" Voices: {len(voices)} ".center(60, "-"))
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = tts.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz
        print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")

  def text_2_audio(
      self,
      text: str,
      output_audio_file_path: str | None = None) -> Text2AudioData:
    """Transform given text into audio.

    Args:
      text: Text to transform.
      output_audio_file_path: Output audio file path to hold the transformed
        result as audio.

    Returns:
      `Text2AudioData` with trasnformed audio information.
    """
    language_code = '-'.join(self._voice_name.split('-')[:2])
    start_time = time.time()
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=self._voice_name)
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.LINEAR16)
    response = self.client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config)
    output_audio_file_path = output_audio_file_path or self._output_path
    with open(output_audio_file_path, 'wb') as out:
      out.write(response.audio_content)

    time_diff_sec = time.time() - start_time
    return Text2AudioData(
        text=text,
        spent_time_sec=time_diff_sec,
        generated_audio_file_path=output_audio_file_path)
