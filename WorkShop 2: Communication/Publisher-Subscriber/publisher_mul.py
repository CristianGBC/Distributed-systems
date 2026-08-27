import zmq
import time
import random


context = zmq.Context()
socket = context.socket(zmq.PUB)


publisher_type = input(
    "Enter publisher service (TIME / WEATHER / NEWS): "
).upper()

serverName = input("Enter server hostname or IP address: ")

if not serverName:
    serverName = "0.0.0.0"

try:
    serverPort = int(input("Enter server port number: "))
except:
    print("Invalid input. Using default port 15000.")
    serverPort = 15000


address = f"tcp://{serverName}:{serverPort}"

socket.bind(address)

print(f"\nPublisher '{publisher_type}' running on {address}")
print("Press Ctrl+C to stop.\n")


counter = 0


try:
    while True:

        time.sleep(3)

        counter += 1

        if publisher_type == "TIME":

            message = (
                f"TIME Current time: {time.asctime()} "
                f"- Message #{counter}"
            )

        elif publisher_type == "WEATHER":

            temperature = random.randint(15, 30)

            conditions = random.choice([
                "Sunny",
                "Cloudy",
                "Rainy",
                "Windy"
            ])

            message = (
                f"WEATHER Temperature: {temperature} C, "
                f"Condition: {conditions} "
                f"- Message #{counter}"
            )

        elif publisher_type == "NEWS":

            news = random.choice([
                "New technology announced",
                "University event scheduled",
                "New research published",
                "Sports event this weekend"
            ])

            message = (
                f"NEWS {news} "
                f"- Message #{counter}"
            )

        else:

            print("Unknown publisher type.")
            break


        socket.send_string(message)

        print("Sent:", message)


except KeyboardInterrupt:

    print("\nPublisher stopped.")


finally:

    socket.close()
    context.term()