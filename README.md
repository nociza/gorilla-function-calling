Deciding which workspace information to collect

Collecting workspace information

Filtering to most relevant information

Sure, here's a basic README for your project:

```markdown
# LLM Function Calling

This is a FastAPI application that uses the Gorilla OpenFunctions API for model inference.

## Project Structure

```
.gitignore
Dockerfile
endpoint/
	lib.py
	main.py
	models.py
poetry.lock
pyproject.toml
scripts/
	start.sh
```

## Setup

This project uses Poetry for dependency management and is Dockerized for easy setup and deployment.

### Local Setup

1. Install the project dependencies:

```sh
poetry install
```

2. Start the FastAPI server:

```sh
uvicorn endpoint.main:app --reload
```

### Docker Setup

1. Build the Docker image:

```sh
docker build -t llm-function-calling .
```

2. Run the Docker container:

```sh
docker run -p 8000:8000 llm-function-calling
```

The application will be available at `http://localhost:8000`.

## Usage

The application exposes two endpoints:

- `GET /`: Returns a welcome message.
- `POST /generate-function-calls`: Processes a `UserQuery` and returns the result of the model inference.