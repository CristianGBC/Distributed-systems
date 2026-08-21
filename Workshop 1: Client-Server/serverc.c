#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

#define BUFFER_SIZE 1024


typedef struct {
    int clientSocket;
    struct sockaddr_in clientAddr;
} ClientData;


void *handle_client(void *arg) {

    ClientData *client = (ClientData *)arg;

    int connectionSocket = client->clientSocket;
    struct sockaddr_in addr = client->clientAddr;

    char buffer[BUFFER_SIZE];

    printf(
        "From Client: %s:%d\n",
        inet_ntoa(addr.sin_addr),
        ntohs(addr.sin_port)
    );


    // Receive customer data
    int bytesReceived = recv(
        connectionSocket,
        buffer,
        BUFFER_SIZE - 1,
        0
    );

    if (bytesReceived < 0) {
        perror("Error receiving data");

        close(connectionSocket);
        free(client);

        return NULL;
    }

    // End the chain
    buffer[bytesReceived] = '\0';

    printf("I received: %s\n", buffer);


    // Convert the message to uppercase.
    for (int i = 0; buffer[i] != '\0'; i++) {
        buffer[i] = toupper((unsigned char)buffer[i]);
    }


    sleep(3);


    // Send the response to the customer.
    if (send(
            connectionSocket,
            buffer,
            strlen(buffer),
            0
        ) < 0) {

        perror("Error sending data");
    }


    // Close the connection with the client.
    close(connectionSocket);

    free(client);

    return NULL;
}


int main() {

    int serverPort;

    printf("Enter server port number: ");

    if (scanf("%d", &serverPort) != 1) {
        printf("Invalid input. Using default port 12000.\n");

        serverPort = 12000;
    }


    // Validate the port number.
    if (serverPort <= 0 || serverPort > 65535) {
        serverPort = 12000;
    }


    // Create a TCP socket.
    int serverSocket = socket(
        AF_INET,
        SOCK_STREAM,
        0
    );

    if (serverSocket < 0) {
        perror("Error creating socket");

        return 1;
    }


    struct sockaddr_in serverAddr;

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(serverPort);


    // Bind the socket to the specified port.
    if (bind(
            serverSocket,
            (struct sockaddr *)&serverAddr,
            sizeof(serverAddr)
        ) < 0) {

        perror("Error binding socket");

        close(serverSocket);

        return 1;
    }


    // Listen for incoming connections.
    if (listen(serverSocket, 1) < 0) {
        perror("Error listening");

        close(serverSocket);

        return 1;
    }


    printf("The server is ready to receive\n");


    // Accept incoming connections in a loop.
    while (1) {

        ClientData *client = malloc(sizeof(ClientData));

        if (client == NULL) {
            perror("Memory allocation error");

            continue;
        }


        socklen_t clientLength = sizeof(client->clientAddr);


        // Accept a new client connection.
        client->clientSocket = accept(
            serverSocket,
            (struct sockaddr *)&client->clientAddr,
            &clientLength
        );


        if (client->clientSocket < 0) {
            perror("Error accepting connection");

            free(client);

            continue;
        }


        // Create a new thread to handle the client.
        pthread_t clientThread;

        if (pthread_create(
                &clientThread,
                NULL,
                handle_client,
                client
            ) != 0) {

            perror("Error creating thread");

            close(client->clientSocket);
            free(client);

            continue;
        }


        // Detach the thread to allow it to clean up after itself.
        pthread_detach(clientThread);
    }


    close(serverSocket);

    return 0;
}
