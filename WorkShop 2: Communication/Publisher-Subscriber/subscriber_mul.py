import zmq


context = zmq.Context()

socket = context.socket(zmq.SUB)


serverName = input(
    "Enter publisher hostname or IP address: "
)

if not serverName:
    serverName = "localhost"


print("\nAvailable services:")
print("1. TIME")
print("2. WEATHER")
print("3. NEWS")
print("4. ALL")

option = input("\nSelect subscription: ")


if option == "1":

    socket.connect(
        f"tcp://{serverName}:15000"
    )

    socket.setsockopt_string(
        zmq.SUBSCRIBE,
        "TIME"
    )


elif option == "2":

    socket.connect(
        f"tcp://{serverName}:15001"
    )

    socket.setsockopt_string(
        zmq.SUBSCRIBE,
        "WEATHER"
    )


elif option == "3":

    socket.connect(
        f"tcp://{serverName}:15002"
    )

    socket.setsockopt_string(
        zmq.SUBSCRIBE,
        "NEWS"
    )


elif option == "4":

    socket.connect(
        f"tcp://{serverName}:15000"
    )

    socket.connect(
        f"tcp://{serverName}:15001"
    )

    socket.connect(
        f"tcp://{serverName}:15002"
    )

    socket.setsockopt_string(
        zmq.SUBSCRIBE,
        "TIME"
    )

    socket.setsockopt_string(
        zmq.SUBSCRIBE,
        "WEATHER"
    )

    socket.setsockopt_string(
        zmq.SUBSCRIBE,
        "NEWS"
    )


else:

    print("Invalid option.")

    socket.close()
    context.term()

    exit()


print("\nSubscriber started.")
print("Waiting for messages...\n")


try:

    while True:

        message = socket.recv_string()

        print("Received:", message)


except KeyboardInterrupt:

    print("\nSubscriber stopped.")


finally:

    socket.close()
    context.term()