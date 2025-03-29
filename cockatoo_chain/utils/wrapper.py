"""Wrapper for pre-defined API interfaces of model A, B and C packages."""

import dataclasses
import enum
from typing import Protocol


@dataclasses.dataclass
class Audio2TextData:
  """Audio to text result or known as Model A's output."""
  text: str
  spent_time_sec: float
  audio_file_path: str


@dataclasses.dataclass
class Text2AudioData:
  """Text to audio result or known as Model C's output."""
  text: str
  spent_time_sec: float
  generated_audio_file_path: str


@enum.unique
class LangEnum(enum.Enum):
  """Supported language enumeration."""

  en = 0
  cn = 1
  multi_lang = -1

  @classmethod
  def from_str(cls, lang_str: str):
    """Transforms input string into corresponding `LangEnum`.

    Rasies:
      ValueError: Invalid input string.
    """
    for supported_lang_enum in cls:
      if supported_lang_enum.name == lang_str:
        return supported_lang_enum

    raise ValueError(f'Unknown lang setting={lang_str}!')


class ModelA(Protocol):
  """Model A interface."""

  def __init__(self, lang: LangEnum = LangEnum.en):
    self.lang = lang

  @property
  def name(self) -> str:
    """Model/Approch name."""
    pass

  def live_2_text(
      self,
      record_time_sec: int = 5,
      output_audio_file_path: str | None = None) -> Audio2TextData:
    """Records and transform audio into text.

    Args:
      record_time_sec: Recording time in seconds.
      output_audio_file_path: Output audio fie path.

    Returns:
      `Audio2TextData` with trasnformed text.
    """
    pass

  def audio_2_text(self, audio_file_path: str) -> Audio2TextData:
    """Turns audio of given file path into text.

    Args:
      audio_file_path: Audio file path to do audio to text transformation.

    Returns:
      `Audio2TextData` with trasnformed text.
    """
    pass


class ModelC(Protocol):
  """Model C interface."""

  def __init__(self, lang: LangEnum = LangEnum.en):
    self.lang = lang

  @property
  def name(self) -> str:
    """Model/Approch name."""
    pass

  def speak_text(
      self,
      text: str) -> None:
    """Speaks out the given text.

    Args:
      text: Text to speak.
    """
    pass

  def text_2_audio(
      self,
      text: str,
      output_audio_file_path: str) -> Text2AudioData:
    """Transform given text into audio.

    Args:
      text: Text to transform.
      output_audio_file_path: Output audio file path to hold the transformed
        result as audio.

    Returns:
      `Text2AudioData` with trasnformed audio information.
    """
    pass
