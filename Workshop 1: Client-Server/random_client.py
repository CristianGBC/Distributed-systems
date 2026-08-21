from socket import *
import random
import string


def generate_random_sentence():
    length = random.randint(5, 15)
    characters = string.ascii_lowercase + " "

    sentence = ""

    for i in range(length):
        sentence += random.choice(characters)

    return sentence


def main():
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

    # Generate a random number of messages
    numberOfMessages = random.randint(3, 8)

    print(f"Number of messages to send: {numberOfMessages}")

    for i in range(numberOfMessages):

        # Create a new connection for each message
        clientSocket = socket(AF_INET, SOCK_STREAM)

        try:
            clientSocket.connect((serverName, serverPort))
        except Exception as e:
            print("Connection error:", e)
            clientSocket.close()
            continue

        # Generate a random message
        sentence = generate_random_sentence()

        print(
            f"Message {i + 1}/{numberOfMessages} - Sending:",
            sentence
        )

        try:
            clientSocket.send(sentence.encode())

            modifiedSentence = clientSocket.recv(1024)

            print(
                f"Message {i + 1}/{numberOfMessages} - From Server:",
                modifiedSentence.decode()
            )

        except Exception as e:
            print("Communication error:", e)

        try:
            clientSocket.close()
        except Exception as e:
            print("Error closing connection:", e)

    print("All messages were sent.")


if __name__ == "__main__":
    main()