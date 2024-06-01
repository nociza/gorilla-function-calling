# `python-base` sets up all our shared environment variables
FROM python:3.10.11 as python-base

# python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    POETRY_VERSION=1.4.0 \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="/root/.local/bin:$VENV_PATH/bin:$PATH"

# `production` image used for runtime
FROM python-base as production

ENV FASTAPI_ENV=production

# Install dependencies for installing poetry and huggingface-cli
RUN apt-get update && apt-get install -y curl git

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN pip install -U "huggingface_hub[cli]"

# Set the working directory for setting up Python project
WORKDIR $PYSETUP_PATH

# Copy project requirement files
COPY poetry.lock pyproject.toml ./

RUN poetry install 

COPY . /function-calling/

# Set the working directory for the application
WORKDIR /function-calling

# Download the model using Hugging Face CLI
RUN mkdir -p /function-calling/models
    
RUN huggingface-cli download gorilla-llm/gorilla-openfunctions-v2-gguf gorilla-openfunctions-v2-q4_K_M.gguf --local-dir /function-calling/models

# Copy the application code
COPY . .

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "endpoint.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
