import zmq


# Server configuration

port_input = input(
    "Enter resource manager port [8000]: "
).strip()

if not port_input:
    port = 8000
else:
    try:
        port = int(port_input)

        if port < 1 or port > 65535:
            raise ValueError

    except ValueError:
        print(
            "Invalid port. Using default port 8000."
        )
        port = 8000



# Shared resource state
resource_owner = None



# Resource Manager

def resource_manager():

    global resource_owner

    context = zmq.Context()
    socket = context.socket(zmq.REP)

    try:

        address = f"tcp://*:{port}"

        socket.bind(address)

        print(
            f"\nResource Manager running "
            f"on port {port}..."
        )

        while True:

            message = socket.recv_json()

            process_id = message.get(
                "process_id"
            )

            action = message.get(
                "action"
            )

            print(
                f"\nRequest from Process "
                f"{process_id}: {action}"
            )

     
            # REQUEST RESOURCE

            if action == "REQUEST":

                if resource_owner is None:

                    resource_owner = process_id

                    print(
                        f"Resource granted to "
                        f"Process {process_id}"
                    )

                    socket.send_json(
                        {
                            "status": "GRANTED"
                        }
                    )

                else:

                    print(
                        f"Resource busy. "
                        f"Currently owned by "
                        f"Process {resource_owner}"
                    )

                    socket.send_json(
                        {
                            "status": "BUSY",
                            "owner": resource_owner
                        }
                    )

  
            # RELEASE RESOURCE

            elif action == "RELEASE":

                if resource_owner == process_id:

                    resource_owner = None

                    print(
                        f"Process {process_id} "
                        f"released the resource"
                    )

                    socket.send_json(
                        {
                            "status": "RELEASED"
                        }
                    )

                else:

                    socket.send_json(
                        {
                            "status":
                            "NOT_OWNER"
                        }
                    )


            # UNKNOWN ACTION

            else:

                socket.send_json(
                    {
                        "status":
                        "INVALID_ACTION"
                    }
                )

    except KeyboardInterrupt:

        print(
            "\nResource Manager stopped."
        )

    except zmq.ZMQError as e:

        print(
            f"ZeroMQ error: {e}"
        )

    except Exception as e:

        print(
            f"Unexpected error: {e}"
        )

    finally:

        socket.close()
        context.term()


# Main

if __name__ == "__main__":

    resource_manager()