"""Module to hold base class or protocols used in model C."""
import enum
from typing import Any
from cockatoo_chain.utils import wrapper
from cockatoo_chain.utils.model_c import gcp


LangEnum = wrapper.LangEnum
ModelC = wrapper.ModelC


class ModelType(enum.StrEnum):
  """Model C types."""

  GCP_TEXT_2_SPEECH = 'gcp_text_2_speech'


def get(
    model_type: ModelType | str,
    settings: dict[str, Any] | None = None) -> wrapper.ModelC:
  """Gets model C.

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
    case ModelType.GCP_TEXT_2_SPEECH:
      return gcp.GCPText2SpeechWrapper(settings)

  raise ValueError(f'Unknown model type="{model_type}')
