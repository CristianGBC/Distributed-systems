#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define BUFFER_SIZE 1024
#define DEFAULT_PORT 12000


// Generate a random sentence between 5 and 15 characters
void generate_random_sentence(char *sentence) {

    int length = (rand() % 11) + 5;

    char characters[] = "abcdefghijklmnopqrstuvwxyz ";

    int numberOfCharacters = strlen(characters);

    for (int i = 0; i < length; i++) {
        sentence[i] = characters[rand() % numberOfCharacters];
    }

    sentence[length] = '\0';
}


int main() {

    char serverName[100];
    int serverPort;

    // Initialize random number generator
    srand(time(NULL));


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

        printf("Invalid input. Using default port 12000.\n");

        serverPort = DEFAULT_PORT;
    }


    if (serverPort <= 0 || serverPort > 65535) {
        serverPort = DEFAULT_PORT;
    }


    // Generate random number of messages between 3 and 8
    int numberOfMessages = (rand() % 6) + 3;

    printf(
        "Number of messages to send: %d\n",
        numberOfMessages
    );


    for (int i = 0; i < numberOfMessages; i++) {

        // Create a new socket for each message
        int clientSocket = socket(
            AF_INET,
            SOCK_STREAM,
            0
        );


        if (clientSocket < 0) {
            perror("Error creating socket");
            continue;
        }


        // Configure server address
        struct sockaddr_in serverAddr;

        memset(&serverAddr, 0, sizeof(serverAddr));

        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(serverPort);


        // Convert server IP address
        if (inet_pton(
                AF_INET,
                serverName,
                &serverAddr.sin_addr
            ) <= 0) {

            printf("Invalid server address\n");

            close(clientSocket);

            continue;
        }


        // Connect to server
        if (connect(
                clientSocket,
                (struct sockaddr *)&serverAddr,
                sizeof(serverAddr)
            ) < 0) {

            perror("Connection error");

            close(clientSocket);

            continue;
        }


        // Generate random message
        char sentence[BUFFER_SIZE];

        generate_random_sentence(sentence);


        printf(
            "Message %d/%d - Sending: %s\n",
            i + 1,
            numberOfMessages,
            sentence
        );


        // Send message
        if (send(
                clientSocket,
                sentence,
                strlen(sentence),
                0
            ) < 0) {

            perror("Communication error");

            close(clientSocket);

            continue;
        }


        // Receive server response
        char modifiedSentence[BUFFER_SIZE];

        int bytesReceived = recv(
            clientSocket,
            modifiedSentence,
            BUFFER_SIZE - 1,
            0
        );


        if (bytesReceived < 0) {

            perror("Communication error");

        } else {

            modifiedSentence[bytesReceived] = '\0';

            printf(
                "Message %d/%d - From Server: %s\n",
                i + 1,
                numberOfMessages,
                modifiedSentence
            );
        }


        // Close connection
        close(clientSocket);
    }


    printf("All messages were sent.\n");

    return 0;
}