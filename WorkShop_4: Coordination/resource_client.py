import zmq


# Process configuration

process_input = input(
    "Enter process ID: "
).strip()

try:
    process_id = int(process_input)

    if process_id <= 0:
        raise ValueError

except ValueError:
    print("Invalid process ID. Using Process 1.")
    process_id = 1


# Server configuration

hostname = input(
    "Enter Resource Manager host [localhost]: "
).strip()

if not hostname:
    hostname = "localhost"


port_input = input(
    "Enter Resource Manager port [8000]: "
).strip()

if not port_input:
    server_port = 8000

else:
    try:
        server_port = int(port_input)

        if server_port < 1 or server_port > 65535:
            raise ValueError

    except ValueError:
        print(
            "Invalid port. Using default port 8000."
        )
        server_port = 8000




# Send request to Resource Manager

def send_request(action):

    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    socket.setsockopt(zmq.RCVTIMEO, 3000)
    socket.setsockopt(zmq.SNDTIMEO, 3000)
    socket.setsockopt(zmq.LINGER, 0)

    try:

        address = (
            f"tcp://{hostname}:{server_port}"
        )

        socket.connect(address)

        message = {
            "process_id": process_id,
            "action": action
        }

        socket.send_json(message)

        response = socket.recv_json()

        return response

    except zmq.Again:

        print(
            "Resource Manager did not respond."
        )

        return None

    except zmq.ZMQError as e:

        print(
            f"ZeroMQ error: {e}"
        )

        return None

    except Exception as e:

        print(
            f"Unexpected error: {e}"
        )

        return None

    finally:

        socket.close()
        context.term()



# Request resource


def request_resource():

    print(
        f"\nProcess {process_id} "
        f"is requesting the resource..."
    )

    response = send_request("REQUEST")

    if response is None:
        return

    status = response.get("status")

    if status == "GRANTED":

        print(
            f"ACCESS GRANTED to "
            f"Process {process_id}"
        )

        print(
            "Process entered the "
            "critical section."
        )

    elif status == "BUSY":

        owner = response.get("owner")

        print(
            f"ACCESS DENIED - Resource busy."
        )

        print(
            f"Currently owned by "
            f"Process {owner}."
        )

    else:

        print(
            f"Unexpected response: {status}"
        )



# Release resource

def release_resource():

    print(
        f"\nProcess {process_id} "
        f"is releasing the resource..."
    )

    response = send_request("RELEASE")

    if response is None:
        return

    status = response.get("status")

    if status == "RELEASED":

        print(
            f"Resource released by "
            f"Process {process_id}."
        )

    elif status == "NOT_OWNER":

        print(
            f"Process {process_id} "
            f"does not own the resource."
        )

    else:

        print(
            f"Unexpected response: {status}"
        )



# Main

if __name__ == "__main__":

    print(
        f"\nProcess {process_id} started."
    )

    try:

        while True:

            print("\n----------------------------")
            print("1. Request resource")
            print("2. Release resource")
            print("3. Exit")
            print("----------------------------")

            option = input(
                "Choose an option: "
            ).strip()

            if option == "1":

                request_resource()

            elif option == "2":

                release_resource()

            elif option == "3":

                print(
                    f"\nProcess {process_id} is exiting..."
                )

                # Try to release the resource before exiting
                response = send_request("RELEASE")

                if response is not None:

                    status = response.get("status")

                    if status == "RELEASED":

                        print(
                            f"Resource automatically released "
                            f"by Process {process_id}."
                        )

                    elif status == "NOT_OWNER":

                        print(
                            f"Process {process_id} did not own "
                            f"the resource."
                        )

                print(
                    f"Process {process_id} stopped."
                )

                break

            else:

                print(
                    "Invalid option."
                )

    except KeyboardInterrupt:

        print(
            f"\nProcess {process_id} stopped."
        )


        