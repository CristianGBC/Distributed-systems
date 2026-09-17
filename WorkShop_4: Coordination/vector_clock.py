import zmq
import threading
import json
import time


# ==========================================
# Process configuration
# ==========================================

NUM_PROCESSES = 3


process_input = input(
    "Enter process ID [1-3]: "
).strip()


try:
    process_id = int(process_input)

    if process_id < 1 or process_id > NUM_PROCESSES:
        raise ValueError

except ValueError:
    print("Invalid process ID. Using Process 1.")
    process_id = 1


# ==========================================
# Port configuration
# ==========================================

default_port = 7000 + process_id

port_input = input(
    f"Enter listening port [{default_port}]: "
).strip()


if not port_input:
    port = default_port

else:

    try:
        port = int(port_input)

        if port < 1 or port > 65535:
            raise ValueError

    except ValueError:
        print(
            f"Invalid port. Using default port "
            f"{default_port}."
        )

        port = default_port


# ==========================================
# Vector clock
# ==========================================

vector_clock = [0] * NUM_PROCESSES

# ==========================================
# Process list
# ==========================================

processes = {
    1: ("localhost", 7001),
    2: ("localhost", 7002),
    3: ("localhost", 7003),
}

# ==========================================
# Local event
# ==========================================

def local_event():

    vector_clock[process_id - 1] += 1

    print(
        f"\nProcess {process_id} LOCAL EVENT"
    )

    print(
        f"Vector clock: {vector_clock}"
    )

# ==========================================
# Message listener
# ==========================================

def message_listener():

    context = zmq.Context()
    socket = context.socket(zmq.REP)

    try:
        address = f"tcp://*:{port}"
        socket.bind(address)

        print(
            f"Process {process_id} listening "
            f"on port {port}..."
        )

        while True:

            # Receive message
            message_json = socket.recv_string()

            message = json.loads(message_json)

            sender_id = message["sender"]
            text = message["text"]
            received_clock = message["clock"]

            print(
                f"\nMessage received from "
                f"Process {sender_id}: {text}"
            )

            print(
                f"Received vector clock: "
                f"{received_clock}"
            )

            # Update vector clock
            for i in range(NUM_PROCESSES):

                vector_clock[i] = max(
                    vector_clock[i],
                    received_clock[i]
                )

            # Increment receiver's own position
            vector_clock[process_id - 1] += 1

            print(
                f"Updated vector clock: "
                f"{vector_clock}"
            )

            # Confirm reception
            socket.send_string("ACK")

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

# ==========================================
# Send message
# ==========================================

def send_message(target_id, text):

    if target_id not in processes:
        print("Invalid target process.")
        return

    if target_id == process_id:
        print(
            "A process cannot send a message "
            "to itself."
        )
        return

    host, target_port = processes[target_id]

    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    socket.setsockopt(zmq.RCVTIMEO, 3000)
    socket.setsockopt(zmq.SNDTIMEO, 3000)
    socket.setsockopt(zmq.LINGER, 0)

    try:

        # Sending is an event:
        # increment own position
        vector_clock[process_id - 1] += 1

        message = {
            "sender": process_id,
            "text": text,
            "clock": vector_clock.copy()
        }

        address = f"tcp://{host}:{target_port}"

        socket.connect(address)

        print(
            f"\nProcess {process_id} sending "
            f"message to Process {target_id}"
        )

        print(
            f"Sending vector clock: "
            f"{vector_clock}"
        )

        socket.send_string(
            json.dumps(message)
        )

        response = socket.recv_string()

        print(
            f"Process {target_id} response: "
            f"{response}"
        )

    except zmq.Again:

        print(
            f"Process {target_id} "
            f"did not respond."
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

# ==========================================
# Main
# ==========================================
# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    print(
        f"\nProcess {process_id} started"
    )

    print(
        f"Listening port: {port}"
    )

    print(
        f"Initial vector clock: "
        f"{vector_clock}"
    )

    # Start message listener
    listener_thread = threading.Thread(
        target=message_listener,
        daemon=True
    )

    listener_thread.start()

    time.sleep(1)

    # Interactive menu
    try:

        while True:

            print("\n----------------------------")
            print("1. Local event")
            print("2. Send message")
            print("3. Show vector clock")
            print("4. Exit")
            print("----------------------------")

            option = input(
                "Choose an option: "
            ).strip()

            if option == "1":

                local_event()

            elif option == "2":

                try:
                    target_id = int(
                        input(
                            "Target process ID: "
                        )
                    )

                except ValueError:
                    print(
                        "Invalid process ID."
                    )
                    continue

                text = input(
                    "Message: "
                )

                send_message(
                    target_id,
                    text
                )

            elif option == "3":

                print(
                    f"\nProcess {process_id} "
                    f"vector clock: "
                    f"{vector_clock}"
                )

            elif option == "4":

                print(
                    f"Process {process_id} "
                    f"stopped."
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