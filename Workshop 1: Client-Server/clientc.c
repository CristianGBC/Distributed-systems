#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

#define BUFFER_SIZE 1024
#define DEFAULT_PORT 12000


// Data needed by each client thread
typedef struct {
    int client_id;
    char serverName[100];
    int serverPort;
} ClientData;


// Each thread executes an independent client
void *handle_client(void *arg) {

    ClientData *data = (ClientData *)arg;

    int client_id = data->client_id;
    int serverPort = data->serverPort;

    char serverName[100];
    strcpy(serverName, data->serverName);

    char sentence[BUFFER_SIZE];
    char modifiedSentence[BUFFER_SIZE];


    // Create client socket
    int clientSocket = socket(AF_INET, SOCK_STREAM, 0);

    if (clientSocket < 0) {
        perror("Error creating socket");
        free(data);
        return NULL;
    }


    // Configure server address
    struct sockaddr_in serverAddr;

    memset(&serverAddr, 0, sizeof(serverAddr));

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(serverPort);


    // Convert IP address
    if (inet_pton(AF_INET, serverName, &serverAddr.sin_addr) <= 0) {

        printf(
            "Client %d - Invalid server address\n",
            client_id
        );

        close(clientSocket);
        free(data);

        return NULL;
    }


    // Connect to server
    if (connect(
            clientSocket,
            (struct sockaddr *)&serverAddr,
            sizeof(serverAddr)
        ) < 0) {

        printf(
            "Client %d - Connection error\n",
            client_id
        );

        close(clientSocket);
        free(data);

        return NULL;
    }


    // Create message: "hello from client X"
    snprintf(
        sentence,
        BUFFER_SIZE,
        "hello from client %d",
        client_id
    );


    printf(
        "Client %d - Sending: %s\n",
        client_id,
        sentence
    );


    // Send message
    if (send(
            clientSocket,
            sentence,
            strlen(sentence),
            0
        ) < 0) {

        printf(
            "Client %d - Communication error\n",
            client_id
        );

        close(clientSocket);
        free(data);

        return NULL;
    }


    // Receive server response
    int bytesReceived = recv(
        clientSocket,
        modifiedSentence,
        BUFFER_SIZE - 1,
        0
    );


    if (bytesReceived < 0) {

        printf(
            "Client %d - Communication error\n",
            client_id
        );

    } else if (bytesReceived == 0) {

        printf(
            "Client %d - Server closed the connection\n",
            client_id
        );

    } else {

        modifiedSentence[bytesReceived] = '\0';

        printf(
            "Client %d - From Server: %s\n",
            client_id,
            modifiedSentence
        );
    }


    // Close client socket
    close(clientSocket);

    free(data);

    return NULL;
}


int main() {

    char serverName[100];
    int serverPort;
    int numberOfClients;


    // Get server IP address
    printf("Enter server hostname or IP address: ");

    fgets(serverName, sizeof(serverName), stdin);

    serverName[strcspn(serverName, "\n")] = '\0';


    // Use localhost by default
    if (strlen(serverName) == 0) {
        strcpy(serverName, "127.0.0.1");
    }


    // Get server port
    printf("Enter server port number: ");

    if (scanf("%d", &serverPort) != 1) {

        printf(
            "Invalid input. Using default port 12000.\n"
        );

        serverPort = DEFAULT_PORT;
    }


    if (serverPort <= 0 || serverPort > 65535) {
        serverPort = DEFAULT_PORT;
    }


    // Get number of clients
    printf("Enter number of clients: ");

    if (scanf("%d", &numberOfClients) != 1) {

        printf(
            "Invalid input. Using 2 clients.\n"
        );

        numberOfClients = 2;
    }


    if (numberOfClients < 2) {

        printf(
            "At least 2 clients are required. Using 2 clients.\n"
        );

        numberOfClients = 2;
    }


    // Create array for threads
    pthread_t *threads = malloc(
        numberOfClients * sizeof(pthread_t)
    );

    if (threads == NULL) {
        perror("Memory allocation error");
        return 1;
    }


    // Create one thread for each client
    for (int i = 0; i < numberOfClients; i++) {

        ClientData *clientData = malloc(
            sizeof(ClientData)
        );

        if (clientData == NULL) {
            perror("Memory allocation error");
            continue;
        }


        clientData->client_id = i + 1;

        strcpy(
            clientData->serverName,
            serverName
        );

        clientData->serverPort = serverPort;


        if (pthread_create(
                &threads[i],
                NULL,
                handle_client,
                clientData
            ) != 0) {

            printf(
                "Error creating client thread %d\n",
                i + 1
            );

            free(clientData);
        }
    }


    // Wait for all clients to finish
    for (int i = 0; i < numberOfClients; i++) {

        pthread_join(
            threads[i],
            NULL
        );
    }


    free(threads);

    return 0;
}