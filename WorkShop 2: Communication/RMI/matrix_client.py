import xmlrpc.client
import numpy as np


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


proxy = xmlrpc.client.ServerProxy(
    f"http://{serverName}:{serverPort}/RPC2"
)


def read_matrix(name):
    rows = int(input(f"Rows of matrix {name}: "))
    cols = int(input(f"Columns of matrix {name}: "))

    matrix = []

    print(f"Enter matrix {name}:")

    for i in range(rows):
        row = list(
            map(
                float,
                input(f"Row {i + 1}: ").split()
            )
        )

        if len(row) != cols:
            print("Invalid number of elements.")
            return None

        matrix.append(row)

    return matrix


def generate_matrix(name):
    rows = int(input(f"Rows of matrix {name}: "))
    cols = int(input(f"Columns of matrix {name}: "))

    matrix = np.random.randint(
        1,
        10,
        size=(rows, cols)
    )

    return matrix.tolist()


def create_matrix(name):

    print()
    print(f"Matrix {name}")
    print("1. Enter manually")
    print("2. Generate randomly")

    option = input("Option: ")

    if option == "1":
        return read_matrix(name)

    elif option == "2":
        matrix = generate_matrix(name)

        print(f"\nGenerated matrix {name}:")
        print(np.array(matrix))

        return matrix

    else:
        print("Invalid option.")
        return None


def print_result(response):

    if response["success"]:
        result = np.array(response["result"])

        print("\nResult:")
        print(result)

    else:
        print("\nServer error:")
        print(response["error"])


while True:

    print("\n==========================")
    print(" Distributed Matrix Manager")
    print("==========================")

    print("1. Add matrices")
    print("2. Subtract matrices")
    print("3. Multiply matrices")
    print("4. Exit")

    option = input("Select operation: ")

    if option == "4":
        print("Closing client...")
        break

    if option not in ["1", "2", "3"]:
        print("Invalid option.")
        continue

    matrix_a = create_matrix("A")

    if matrix_a is None:
        continue

    matrix_b = create_matrix("B")

    if matrix_b is None:
        continue


    print("\nMatrix A:")
    print(np.array(matrix_a))

    print("\nMatrix B:")
    print(np.array(matrix_b))


    try:

        if option == "1":

            response = proxy.add_matrices(
                matrix_a,
                matrix_b
            )

        elif option == "2":

            response = proxy.subtract_matrices(
                matrix_a,
                matrix_b
            )

        elif option == "3":

            response = proxy.multiply_matrices(
                matrix_a,
                matrix_b
            )

        print_result(response)

    except ConnectionRefusedError:
        print("Could not connect to server.")

    except Exception as error:
        print("Error:", error)