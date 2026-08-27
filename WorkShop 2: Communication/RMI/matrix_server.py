from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import numpy as np


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

serverName = input("Enter server hostname or IP address: ")

if not serverName:
    serverName = "localhost"

try:
    serverPort = int(input("Enter server port number: "))
except:
    print("Invalid input. Using default port 12000.")
    serverPort = 12000

if serverPort <= 0 or serverPort > 65535:
    serverPort = 12000

# Remote functions

def add_matrices(matrix_a, matrix_b):
    A = np.array(matrix_a)
    B = np.array(matrix_b)

    if A.shape != B.shape:
        return {
            "success": False,
            "error": "Matrices must have the same dimensions."
        }

    result = A + B

    return {
        "success": True,
        "result": result.tolist()
    }


def subtract_matrices(matrix_a, matrix_b):
    A = np.array(matrix_a)
    B = np.array(matrix_b)

    if A.shape != B.shape:
        return {
            "success": False,
            "error": "Matrices must have the same dimensions."
        }

    result = A - B

    return {
        "success": True,
        "result": result.tolist()
    }


def multiply_matrices(matrix_a, matrix_b):
    A = np.array(matrix_a)
    B = np.array(matrix_b)

    if A.shape[1] != B.shape[0]:
        return {
            "success": False,
            "error": "Invalid dimensions for matrix multiplication."
        }

    result = np.matmul(A, B)

    return {
        "success": True,
        "result": result.tolist()
    }


# Server

with SimpleXMLRPCServer(
    (serverName, serverPort),
    requestHandler=RequestHandler,
    allow_none=True
) as server:

    server.register_introspection_functions()

    server.register_function(add_matrices, "add_matrices")
    server.register_function(subtract_matrices, "subtract_matrices")
    server.register_function(multiply_matrices, "multiply_matrices")

    print(f"Matrix server listening on {serverName}:{serverPort}...")

    server.serve_forever()