"""Base module of Model A."""
from cockatoo_chain.utils import wrapper


Audio2TextData = wrapper.Audio2TextData


class ModelBase(wrapper.ModelA):
  """Base model A."""

  def live_2_text(
      self,
      record_time_sec: int = 5,
      output_audio_file_path: str | None = None) -> Audio2TextData:
    """Records and transform audio into text.

    Let child class to implement.

    Returns:
      `Audio2TextData` with trasnformed text.
    """
    raise NotImplementedError('Child class should implement')
