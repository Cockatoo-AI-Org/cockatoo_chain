"""Base module of Model C."""
import logging
from cockatoo_chain.utils import wrapper


Text2AudioData = wrapper.Text2AudioData


class ModelBase(wrapper.ModelC):
  """Base model C."""

  def speak_text(
      self,
      text: str) -> None:
    """Speaks out the given text.

    Args:
      text: Text to speak.
    """
    result = self.text_2_audio(text)
    logging.info('Play audio from %s', result.generated_audio_file_path)
    # TBD: Play audio with result.audio_file_path
