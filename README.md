# cockatoo_chain
This repo is intended for STT, LLM and TSS models chaining.


# Development Mode
Development Mode is intended for users who wish to contribute to the repo and thus needs to install additional dev-related packages for, e.g., code quality checking, to satisfy the standard of the repo.
If you hope to contribute to the repository, please follow up the follow instructions:

## Create virtual environment by `poetry`
```shell
# Force poetry to build virtual environment in the repo.
$ poetry config virtualenvs.in-project true

# Create virtual environment
$ poetry env use python

# Confirm the created virtual environment
$ poetry env info
```

## Enter virtual environment and installed packages
```shell
# Get the command to enter virtual environment
$ poetry env activate
$ source activate <your venv>
$ make init-repo-setup
```

# Model A Usage
From `cockagoo_chain` package, you can easily access the power of Model A (Speech-to-text) with a few lines of codes. We will learn how to from this section. For the time being, `cockagoo_chain` support below types of model A:

| Name            | Type       | Supported language                                                                            | Supported file type                                                                                                                     | Note                                                                   |
|-----------------|------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| open_ai_whisper | Remote API | en, cn and [more](https://platform.openai.com/docs/guides/speech-to-text#supported-languages) | File uploads are currently limited to 25 MB, and the following input file types are supported: mp3, mp4, mpeg, mpga, m4a, wav, and webm | [Official doc](https://platform.openai.com/docs/guides/speech-to-text) |
| gcp_stt | Remote API | en, cn and [more](https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages) | For details, please refer to [this link](https://cloud.google.com/speech-to-text/docs/optimizing-audio-files-for-speech-to-text#codecs_recognized_by_speech-to-text) | [Official doc](https://cloud.google.com/speech-to-text?hl=en) |

## Get supported Model A options
You can use below code snippet to get the supported model A options:
```python
>>> from cockatoo_chain.utils import model_a
>>> model_type = model_a.ModelType
>>> list(model_type)
[<ModelType.OPEN_AI_WHISPER: 'open_ai_whisper'>]
```

## Transform input audio file into text
Below code snippet demonstrates how to obtain the OpenAI whipser wrapper for model A and apply it to transform the audio file into text:
```python
>>> test_en_audio_file_path = '~/test_audio_files/en_20240108_johnlee.wav'
>>> model_a_wrapper = model_a.get(model_type.OPEN_AI_WHISPER)
>>> response = model_a_wrapper.audio_2_text(test_en_audio_file_path)
>>> response
Audio2TextData(
    text='Hello, this is for testing in English. We will use this to evaluate model SST...',
    spent_time_sec=7.87896990776062,
    audio_file_path='/root/test_audio_files/en_20240108_johnlee.wav')
>>> response.text
'Hello, this is for testing in English. We will use this to evaluate model SST and see how it performs. Thanks.'
```

# Model C Usage
From `cockagoo_chain` package, you can easily access the power of Model C (Text-to-speech) with a few lines of codes. We will learn how to from this section. For the time being, `cockagoo_chain` support below types of model C:

| Name              | Type       | Supported language                                                                    | Supported output file type | Note                                                         |
|-------------------|------------|---------------------------------------------------------------------------------------|----------------------------|--------------------------------------------------------------|
| gcp_text_2_speech | Remove API | en, cn and [more](https://cloud.google.com/text-to-speech/docs/list-voices-and-types) | wav                        | [Offical doc](https://cloud.google.com/text-to-speech?hl=en) |

## Get supported Model C options
```python
>>> from cockatoo_chain.utils import model_c
>>> mt = model_c.ModelType
>>> list(mt)
[<ModelType.GCP_TEXT_2_SPEECH: 'gcp_text_2_speech'>]
```

## Transform text into speech
Below code snippet demonstrates how to obtain the GCP text-to-speech wrapper as model C and apply it to transform give text into speech and save it as audio file:
```python
>>> mc_imp = model_c.get(mt.GCP_TEXT_2_SPEECH)
>>> mc_imp.name
'GCP/text-to-speech'
>>> mc_imp.text_2_audio("Nice to meet you all and welcome to join Cockatoo-AI's group meeting!")
Text2AudioData(
    text="Nice to meet you all and welcome to join Cockatoo-AI's group meeting!",
    spent_time_sec=1.822951,
    generated_audio_file_path='/tmp/gcp_tts_output.wav')
```
