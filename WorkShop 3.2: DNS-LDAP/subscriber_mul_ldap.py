import zmq
import ldap


# -------------------- LDAP CONFIGURATION --------------------

LDAP_SERVER = "ldap://localhost"
LDAP_BASE_DN = "dc=example,dc=com"
LDAP_SERVICES_DN = f"ou=Services,{LDAP_BASE_DN}"


def find_service(service_name):
    """
    Searches LDAP using the service name and returns:
        (IP address, port)

    The Subscriber does not know the Publisher IP or port beforehand.
    """
    connection = ldap.initialize(LDAP_SERVER)
    connection.set_option(ldap.OPT_NETWORK_TIMEOUT, 5)

    try:
        # Anonymous/simple bind is enough for reading the directory
        # in the default OpenLDAP configuration used in this workshop.
        connection.simple_bind_s("", "")

        search_filter = f"(cn={service_name})"

        results = connection.search_s(
            LDAP_SERVICES_DN,
            ldap.SCOPE_SUBTREE,
            search_filter,
            ["cn", "description"]
        )

        if not results:
            return None

        _, attributes = results[0]

        descriptions = attributes.get(
            "description",
            []
        )

        ip_address = None
        port = None

        for item in descriptions:

            value = item.decode()

            if value.startswith("ip="):
                ip_address = value.split(
                    "=",
                    1
                )[1]

            elif value.startswith("port="):
                port = int(
                    value.split(
                        "=",
                        1
                    )[1]
                )

        if ip_address is None or port is None:
            return None

        return ip_address, port

    finally:
        connection.unbind_s()


# -------------------- ZEROMQ SUBSCRIBER --------------------

context = zmq.Context()
socket = context.socket(zmq.SUB)


print("\nAvailable services:")
print("1. TIME")
print("2. WEATHER")
print("3. NEWS")
print("4. ALL")

option = input("\nSelect subscription: ")


if option == "1":
    requested_services = ["TIME"]

elif option == "2":
    requested_services = ["WEATHER"]

elif option == "3":
    requested_services = ["NEWS"]

elif option == "4":
    requested_services = [
        "TIME",
        "WEATHER",
        "NEWS"
    ]

else:
    print("Invalid option.")
    socket.close()
    context.term()
    exit()


print("\nSearching services in LDAP...\n")


try:

    for service_name in requested_services:

        service = find_service(service_name)

        if service is None:
            print(
                f"Service '{service_name}' "
                "was not found in LDAP."
            )

            socket.close()
            context.term()
            exit()

        ip_address, port = service

        endpoint = (
            f"tcp://{ip_address}:{port}"
        )

        print(
            f"Service found: {service_name}"
        )
        print(
            f"  IP:   {ip_address}"
        )
        print(
            f"  Port: {port}"
        )
        print(
            f"  Connecting to: {endpoint}\n"
        )

        socket.connect(endpoint)

        socket.setsockopt_string(
            zmq.SUBSCRIBE,
            service_name
        )


except ldap.SERVER_DOWN:

    print(
        "Could not connect to LDAP server. "
        "Check that slapd is running."
    )

    socket.close()
    context.term()
    exit()


except ldap.NO_SUCH_OBJECT:

    print(
        "The LDAP Services organizational unit "
        "does not exist."
    )

    socket.close()
    context.term()
    exit()


except ldap.LDAPError as e:

    print(f"LDAP error: {e}")

    socket.close()
    context.term()
    exit()


print("Subscriber started.")
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
