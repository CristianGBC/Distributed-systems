import zmq
import threading
import time


# Process configuration

process_input = input(
    "Enter process ID [1-3]: "
).strip()

try:
    process_id = int(process_input)

    if process_id not in [1, 2, 3]:
        raise ValueError

except ValueError:
    print("Invalid process ID.")
    exit(1)


# Ring configuration

processes = {
    1: ("localhost", 9001),
    2: ("localhost", 9002),
    3: ("localhost", 9003),
}

successor = {
    1: 2,
    2: 3,
    3: 1,
}

host, port = processes[process_id]

next_process = successor[process_id]


# Token state

has_token = process_id == 1
in_critical_section = False

token_lock = threading.Lock()


print(
    f"\nProcess {process_id} configured on port {port}"
)

print(
    f"Next process in ring: Process {next_process}"
)

if has_token:

    print(
        "Initial TOKEN assigned to this process."
    )

else:

    print(
        "Waiting for TOKEN..."
    )


# Token listener

def listen_for_token():

    global has_token

    context = zmq.Context()

    receiver = context.socket(zmq.REP)

    address = f"tcp://*:{port}"

    receiver.bind(address)

    print(
        f"Process {process_id} listening for TOKEN "
        f"on port {port}..."
    )

    try:

        while True:

            message = receiver.recv_json()

            if message.get("type") == "TOKEN":

                sender = message.get("from")

                with token_lock:
                    has_token = True

                print(
                    f"\n>>> TOKEN received from "
                    f"Process {sender} <<<"
                )

                print(
                    f"Process {process_id} now has "
                    f"the TOKEN."
                )

                receiver.send_json(
                    {"status": "TOKEN_RECEIVED"}
                )

            else:

                receiver.send_json(
                    {"status": "INVALID_MESSAGE"}
                )

    except KeyboardInterrupt:

        pass

    finally:

        receiver.close()
        context.term()


# Pass token

def pass_token():

    global has_token

    with token_lock:

        if not has_token:

            print(
                f"\nProcess {process_id} does not have "
                f"the TOKEN."
            )

            return

        if in_critical_section:

            print(
                "\nCannot pass the TOKEN while inside "
                "the critical section."
            )

            return

        has_token = False


    next_host, next_port = processes[next_process]

    context = zmq.Context()

    sender = context.socket(zmq.REQ)

    sender.setsockopt(
        zmq.RCVTIMEO,
        3000
    )

    sender.setsockopt(
        zmq.SNDTIMEO,
        3000
    )

    sender.setsockopt(
        zmq.LINGER,
        0
    )

    address = (
        f"tcp://{next_host}:{next_port}"
    )

    sender.connect(address)

    try:

        print(
            f"\nPassing TOKEN to Process "
            f"{next_process}..."
        )

        sender.send_json(
            {
                "type": "TOKEN",
                "from": process_id
            }
        )

        response = sender.recv_json()

        if response.get("status") == "TOKEN_RECEIVED":

            print(
                f"TOKEN successfully passed to "
                f"Process {next_process}."
            )

    except zmq.Again:

        print(
            f"\nProcess {next_process} "
            f"did not respond."
        )

        with token_lock:
            has_token = True

        print(
            f"Process {process_id} keeps "
            f"the TOKEN."
        )

    finally:

        sender.close()
        context.term()


# Enter critical section

def enter_critical_section():

    global in_critical_section

    with token_lock:

        if not has_token:

            print(
                f"\nACCESS DENIED. Process {process_id} "
                f"does not have the TOKEN."
            )

            return

        if in_critical_section:

            print(
                f"\nProcess {process_id} is already "
                f"inside the critical section."
            )

            return

        in_critical_section = True


    print(
        f"\nACCESS GRANTED to Process {process_id}."
    )

    print(
        "Process entered the critical section."
    )


# Leave critical section

def leave_critical_section():

    global in_critical_section

    with token_lock:

        if not in_critical_section:

            print(
                f"\nProcess {process_id} is not "
                f"inside the critical section."
            )

            return

        in_critical_section = False


    print(
        f"\nProcess {process_id} left "
        f"the critical section."
    )


# Start listener

listener_thread = threading.Thread(
    target=listen_for_token,
    daemon=True
)

listener_thread.start()


print("\nToken Ring process is running.")


# Main menu

try:

    while True:

        print("\nOptions:")
        print("1. Show TOKEN status")
        print("2. Enter critical section")
        print("3. Leave critical section")
        print("4. Pass TOKEN")
        print("5. Exit")

        option = input(
            "Select an option: "
        ).strip()

        if option == "1":

            with token_lock:

                if has_token:

                    print(
                        f"\nProcess {process_id} "
                        f"HAS the TOKEN."
                    )

                else:

                    print(
                        f"\nProcess {process_id} "
                        f"does NOT have the TOKEN."
                    )

        elif option == "2":

            enter_critical_section()

        elif option == "3":

            leave_critical_section()

        elif option == "4":

            pass_token()

        elif option == "5":

            if in_critical_section:

                print(
                    "\nCannot exit while inside "
                    "the critical section."
                )

                continue

            with token_lock:
                owns_token = has_token

            if owns_token:

                print(
                    f"\nProcess {process_id} has the TOKEN."
                )

                print(
                    "Passing TOKEN before exiting..."
                )

                pass_token()

            print(
                f"\nProcess {process_id} stopped."
            )

            break

        else:

            print(
                "\nInvalid option."
            )

except KeyboardInterrupt:

    print(
        f"\nProcess {process_id} stopped."
    )