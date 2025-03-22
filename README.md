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
``
