"""Base module of Model A."""
import logging
import pyaudio
import wave

from cockatoo_chain.utils import wrapper


CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
Audio2TextData = wrapper.Audio2TextData
DEFAULT_OUTPUT_AUDIO_PATH = '/tmp/modela_live_audio.wav'


class ModelBase(wrapper.ModelA):
  """Base model A."""

  def live_2_text(
      self,
      record_time_sec: int = 5,
      output_audio_file_path: str | None = None,
      rate=RATE,
      chunk=CHUNK) -> Audio2TextData:
    """Records and transform audio into text.

    Args:
      record_time_sec: Recording time in seconds.
      output_audio_file_path: Output audio fie path.
      rate: Sample rate for audio recording. Defaults to `RATE`.
      chunk: Number of frames per buffer. Defaults to `CHUNK`.

    Returns:
      `Audio2TextData` with trasnformed text.
    """
    output_audio_file_path = (
        output_audio_file_path or DEFAULT_OUTPUT_AUDIO_PATH)
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=rate,
        input=True,
        frames_per_buffer=chunk)

    logging.info("* recording")
    frames = []

    for i in range(0, int(rate / chunk * record_time_sec)):
      data = stream.read(chunk)
      frames.append(data)

    logging.info("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_audio_file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return self.audio_2_text(output_audio_file_path)
