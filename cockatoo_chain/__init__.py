"""cocktoo_chain base module to get chain of STT+LLM+TTS."""
from __future__ import annotations

import dataclasses
from datetime import datetime
import functools
import os
from dotenv import load_dotenv, find_dotenv
import textwrap
from typing import Any, Callable, TypeAlias

import langchain_core
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from langchain_openai import ChatOpenAI

from cockatoo_chain.utils import wrapper
from cockatoo_chain.utils import model_a
from cockatoo_chain.utils import model_c


ModelC = wrapper.ModelC
ModelA = wrapper.ModelA
RunnableSequence: TypeAlias = langchain_core.runnables.base.RunnableSequence


prompt_str = textwrap.dedent("""
You are a senior engineer working on the Cockatoo.AI open-source project.
You are an expert on how to use the `Cockatoo.AI` GitHub repository.

Answer questions using only the provided context. Be as detailed as possible.
If you don't know the answer, say "I don't know."

From Cockatoo.AI, we have three main members:
- Wen-Kai Chung: He is the host of this project and mainly focus on Model C aka
  Text-To-Speech. Below is his about:
> I am a data scientist with a background in BS mathematics and MS econometrics.
> I received extensive research as well as industry training in the field of
> natural language processing with academic publications, and in the field of
> time series. In total, I have 4+ years of coding experiences
> (C++, Matlab, Python), and 3 years of data science experience. Equipped with
> knowledge in developing and commercializing machine learning methods to solve
> business problems, I am seeking the full-time Data Scientist position.
- Louis Tai-Jui Chang: He is mainly focus on Model B aka LLM.
  Below is his about:
> M.S. in Biomedical Electronics and Bioinformatics (Electronics)⠀|
> Technical Program Manager at Wiwynn. Interest in Cutting-edge Technology,
> Health Policy, and Global Partnerships.
- John Lee: He is mainly focus on Model A aka Speech-To-Text.
  He is currently served in Google as Test Engineer. Below is his about:
> My motto is where there is a will, there is a way.

With above context, please answer below question:
{question}
""").strip()  # noqa: E501
DEFAULT_PROMPT = ChatPromptTemplate.from_template(prompt_str)


def load_env(env_path: str | None = None):
  """Loads environment variables.

  Args:
    env_path: File path to hold customized environment variables.
  """
  env_path = env_path or '~/.env'
  _ = load_dotenv(find_dotenv(os.path.expanduser(env_path)))


load_env()


@dataclasses.dataclass(frozen=True)
class STTConfig:
  model_type: model_a.ModelType = model_a.ModelType.OPEN_AI_WHISPER
  settings: dict[str, Any] = dataclasses.field(default_factory=dict)
  model: ModelA | None = None

  def get_model(self):
    return self.model or model_a.get(self.model_type, self.settings)

  @classmethod
  def default(cls) -> STTConfig:
    return cls()


@dataclasses.dataclass(frozen=True)
class TTSConfig:
  model_type: model_c.ModelType = model_c.ModelType.GCP_TEXT_2_SPEECH
  settings: dict[str, Any] = dataclasses.field(default_factory=dict)
  model: ModelC | None = None

  @classmethod
  def default(cls) -> TTSConfig:
    return cls()

  def get_model(self):
    return self.model or model_c.get(self.model_type, self.settings)


def get(
    stt_config: STTConfig = STTConfig.default(),
    chat_model: Any = None,
    tts_config: TTSConfig = TTSConfig.default(),
    prompt: ChatPromptTemplate = DEFAULT_PROMPT
) -> Callable[[str], dict[str, Any]]:
  """Gets chain of model A, model B and model C.

  Args:
    stt_config: Configuration of model A.
    chat_model: Model B aka LLM model. Default is ChatGPT 3.5.
    tts_config: Configuration of model C
    prompt: Prompt of model B.
  """
  context = {}
  chat_model = chat_model or ChatOpenAI(
    model="gpt-3.5-turbo-0125", temperature=0)

  def _llm_chat(prompt, chat_model, context):
    start_time = datetime.now()
    resp = chat_model.invoke(prompt)
    spent_time_sec = (datetime.now() - start_time).total_seconds()
    context['llm_time_sec'] = spent_time_sec
    context['llm_name'] = chat_model.__class__.__name__
    context['llm_output'] = resp
    return resp

  llm_chat = RunnableLambda(functools.partial(
      _llm_chat,
      chat_model=chat_model,
      context=context))

  def _parse_audio_file(
      data_dict: dict[str, Any],
      stt_model: ModelA,
      context: dict[str, Any]):
    audio_file_path = data_dict['audio_file_path']
    resp = stt_model.audio_2_text(audio_file_path)
    context['stt_name'] = stt_model.name
    context['stt_time_sec'] = resp.spent_time_sec
    context['stt_output'] = resp.text
    return {'question': resp.text}

  parse_audio_file = functools.partial(
      _parse_audio_file,
      stt_model=stt_config.get_model(),
      context=context)
  input_audio_parser = RunnableLambda(parse_audio_file)

  def _output_text_2_audio_file(
      text: str,
      tts_model: ModelC,
      context: dict[str, Any]):
    resp = tts_model.text_2_audio(text)
    context['tts_time_sec'] = resp.spent_time_sec
    context['tts_name'] = tts_model.name
    return resp.generated_audio_file_path

  output_text_2_audio_file = functools.partial(
      _output_text_2_audio_file,
      tts_model=tts_config.get_model(),
      context=context)
  output_audio_file = RunnableLambda(output_text_2_audio_file)

  chain = (
    input_audio_parser     # 1) Turn speech into text
    | prompt               # 2) Put question into context as prompt
    | llm_chat             # 3) Feed in LLM
    | StrOutputParser()    # 4) Format the output
    | output_audio_file    # 5) Turn text into speech
  )

  def _answer(
      input_audio_file_path: str,
      chain: RunnableSequence,
      context: dict[str, Any]):
    resp = chain.invoke({
      'audio_file_path': input_audio_file_path})
    return {'output_audio_file_path': resp} | context

  return functools.partial(_answer, chain=chain, context=context)
