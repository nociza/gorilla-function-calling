from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from functools import partial
from llama_cpp import Llama
from concurrent.futures import ThreadPoolExecutor
import asyncio

from endpoint.models import UserQuery
from endpoint.lib import get_prompt_python_function_call, parse_python_function_call


executor = ThreadPoolExecutor(max_workers=4)

# Initialize the Llama model
llm = Llama(
    model_path="./models/gorilla-openfunctions-v2-q4_K_M.gguf",
    n_threads=8,
    n_gpu_layers=35,
    batch_size=16,  # Set the batch size for batching
    parallel_calls=4,  # Set the number of parallel calls
    verbose=False,
)


async def async_model_inference(prompt):
    loop = asyncio.get_running_loop()
    llm_partial = partial(llm, prompt, max_tokens=512, stop=["<|EOT|>"], echo=True)
    result = await loop.run_in_executor(executor, llm_partial)
    return result


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to my hosting of the Gorilla OpenFunctions API!"}


@app.post("/generate-function-calls")
async def process_query(request: UserQuery):
    try:
        user_prompt = get_prompt_python_function_call(
            request.user_query, request.functions
        )
        output = llm(user_prompt, max_tokens=512, stop=["<|EOT|>"], echo=True)
        functions_raw_string = (
            output["choices"][0]["text"].split("### Response: ")[1].strip()
        )
        functions = functions_raw_string.split("<<function>>")[1:]

        return JSONResponse(content={"functions": functions})
    except Exception as e:
        print(f"Error generating function calls. Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-api-calls")
async def process_query(request: UserQuery):
    try:
        user_prompt = get_prompt_python_function_call(
            request.user_query, request.functions
        )
        output = await async_model_inference(user_prompt)
        functions_raw_string = (
            output["choices"][0]["text"].split("### Response: ")[1].strip()
        )
        functions = functions_raw_string.split("<<function>>")[1:]
        api_calls = []
        for f in functions:
            try:
                api_call = parse_python_function_call(f.strip())
                api_calls.append(api_call)
            except Exception as e:
                print(f"Error parsing function: {f.strip()}. Error: {str(e)}")
        return JSONResponse(content={"api_calls": api_calls})
    except Exception as e:
        print(f"Error generating API calls. Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
