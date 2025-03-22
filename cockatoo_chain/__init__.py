import os
from dotenv import load_dotenv, find_dotenv


def load_env(env_path: str | None = None):
  """Loads environment variables.

  Args:
    env_path: File path to hold customized environment variables.
  """
  env_path = env_path or '~/.env'
  _ = load_dotenv(find_dotenv(os.path.expanduser(env_path)))


load_env()
