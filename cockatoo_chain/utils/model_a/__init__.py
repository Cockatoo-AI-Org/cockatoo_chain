"""Module to hold base class or protocols used in model A."""
import enum
from typing import Any
from cockatoo_chain.utils import wrapper
from cockatoo_chain.utils.model_a import open_ai
from cockatoo_chain.utils.model_a import gcp


LangEnum = wrapper.LangEnum


class ModelType(enum.StrEnum):
  """Model A types."""

  OPEN_AI_WHISPER = 'open_ai_whisper'
  GCP_STT = 'gcp_stt'


def get(
    model_type: ModelType | str,
    settings: dict[str, Any] | None = None) -> wrapper.ModelA:
  """Gets model A.

  Args:
    model_type: Model type.
    settings: Model settings.

  Returns:
    Model A wrapper implementation.

  Raises:
    ValueError: Unexpected `model_type`.
  """
  if not settings:
    settings = {'lang': LangEnum.en}

  match model_type:
    case ModelType.OPEN_AI_WHISPER:
      return open_ai.OpenAIWrapper(settings)
    case ModelType.GCP_STT:
      return gcp.GCPSpeech2TextWrapper(settings)
    case _:
      raise ValueError('Invalid model type="{model_type}"!')
