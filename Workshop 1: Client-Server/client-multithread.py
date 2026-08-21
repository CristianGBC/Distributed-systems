from socket import *
import threading


# Each thread runs an independent client
def handle_client(client_id, serverName, serverPort):
    clientSocket = socket(AF_INET, SOCK_STREAM)

    try:
        clientSocket.connect((serverName, serverPort))
    except Exception as e:
        print(f"Client {client_id} connection error:", e)
        return

    sentence = f"hello from client {client_id}"

    try:
        clientSocket.send(sentence.encode())

        modifiedSentence = clientSocket.recv(1024)

        print(
            f"Client {client_id} - From Server:",
            modifiedSentence.decode()
        )

    except Exception as e:
        print(f"Client {client_id} communication error:", e)

    try:
        clientSocket.close()
    except Exception as e:
        print(f"Client {client_id} closing error:", e)


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

    try:
        numberOfClients = int(input("Enter number of clients: "))
    except:
        print("Invalid input. Using 2 clients.")
        numberOfClients = 2

    if numberOfClients < 2:
        print("At least 2 clients are required. Using 2 clients.")
        numberOfClients = 2

    threads = []

    for i in range(numberOfClients):
        clientThread = threading.Thread(
            target=handle_client,
            args=(i + 1, serverName, serverPort)
        )

        threads.append(clientThread)
        clientThread.start()

    # Wait until all customers are finished
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()