"""Wrapper of package `speech_recognition`."""
import logging
import openai
import os
import time
from cockatoo_chain.utils import wrapper
from cockatoo_chain.utils.model_a import base


Audio2TextData = wrapper.Audio2TextData
ModelBase = base.ModelBase


class OpenAIWrapper(ModelBase):
  """Wrapper of OpenAI speech-to-text APIs.

  For details, please refer to:
  - https://platform.openai.com/docs/guides/speech-to-text

  To use this wrapper, you need to provide OpenAI key in
  environment variable `OPENAI_API_KEY`.

  For the supported languages, please refer to:
  - https://platform.openai.com/docs/guides/speech-to-text#supported-languages

  Attributes:
    client: OpenAI client instance.
  """

  def __init__(
      self, lang: wrapper.LangEnum, model: str = 'whisper-1'):
    super().__init__(lang)
    self._client = openai.OpenAI()
    self._model = model

  @property
  def client(self):
    """Returns OpenAI client."""
    return self._client

  @property
  def name(self) -> str:
    """Returns the name of model A."""
    return 'OpenAI/speech-to-text'

  def audio_2_text(self, audio_file_path: str) -> Audio2TextData:
    """Turns audio from input audio file into text."""
    audio_file_path = os.path.expanduser(audio_file_path)
    start_time = time.time()
    try:
      # Using Whisper API
      transcription = self.client.audio.transcriptions.create(
          model=self._model,
          file=open(audio_file_path, 'rb'))

      audio_text = transcription.text
      time_diff_sec = time.time() - start_time
      return Audio2TextData(
          text=audio_text,
          spent_time_sec=time_diff_sec,
          audio_file_path=audio_file_path)
    except Exception as ex:
      logging.error(
          f'Failed to transform audio to text from {audio_file_path}')
      raise ex
