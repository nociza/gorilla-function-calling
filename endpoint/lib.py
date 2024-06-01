import json
from typing import List
import ast

from endpoint.models import Function


def get_prompt_python_function_call(
    user_query: str, functions: List[Function] = []
) -> str:
    system = "You are an AI api calling assistant, utilizing the Gorilla LLM model, and your job is to assist the user in calling the correct functions. You are given a user query and a list of functions. You need to choose the correct functions to call based on the user query and the list of functions."
    if not functions:
        return f"{system}\n### Instruction: <<question>> {user_query}\n### Response: "
    functions_string = json.dumps([f.dict() for f in functions])
    return f"{system}\n### Instruction: <<function>>{functions_string}\n<<question>>{user_query}\n### Response: "


def process_ast_node(node):
    # Check if the node is a function call
    if isinstance(node, ast.Call):
        # Return a string representation of the function call
        return ast.unparse(node)
    else:
        # Convert the node to source code and evaluate to get the value
        node_str = ast.unparse(node)
        return eval(node_str)


def parse_python_function_call(call_str):
    tree = ast.parse(call_str)
    expr = tree.body[0]

    call_node = expr.value
    function_name = (
        call_node.func.id
        if isinstance(call_node.func, ast.Name)
        else str(call_node.func)
    )

    parameters = {}
    noNameParam = []

    # Process positional arguments
    for arg in call_node.args:
        noNameParam.append(process_ast_node(arg))

    # Process keyword arguments
    for kw in call_node.keywords:
        parameters[kw.arg] = process_ast_node(kw.value)

    if noNameParam:
        parameters["None"] = noNameParam

    function_dict = {"name": function_name, "arguments": parameters}
    return function_dict
