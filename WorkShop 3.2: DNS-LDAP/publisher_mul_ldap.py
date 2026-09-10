import zmq
import time
import random
import socket as network_socket
import getpass
import ldap
import ldap.modlist as modlist


# -------------------- LDAP CONFIGURATION --------------------

LDAP_SERVER = "ldap://localhost"
LDAP_BASE_DN = "dc=example,dc=com"
LDAP_SERVICES_DN = f"ou=Services,{LDAP_BASE_DN}"
LDAP_ADMIN_DN = f"cn=admin,{LDAP_BASE_DN}"


def get_local_ip():
    """
    Gets an IP address that other computers on the same network can use.
    This is important because 0.0.0.0 is only used for binding locally;
    it is not an address that a remote Subscriber can connect to.
    """
    sock = network_socket.socket(
        network_socket.AF_INET,
        network_socket.SOCK_DGRAM
    )

    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def ensure_services_ou(connection):
    """
    Creates ou=Services if it does not exist yet.
    """
    attributes = {
        "objectClass": [b"organizationalUnit"],
        "ou": [b"Services"]
    }

    ldif = modlist.addModlist(attributes)

    try:
        connection.add_s(LDAP_SERVICES_DN, ldif)
        print(f"LDAP organizational unit created: {LDAP_SERVICES_DN}")
    except ldap.ALREADY_EXISTS:
        pass


def register_service(service_name, ip_address, port, admin_password):
    """
    Registers or updates a service in LDAP.

    Example LDAP entry:
        cn=TIME,ou=Services,dc=example,dc=com
        description: ip=192.168.1.10
        description: port=15000
    """
    connection = ldap.initialize(LDAP_SERVER)
    connection.set_option(ldap.OPT_NETWORK_TIMEOUT, 5)

    try:
        connection.simple_bind_s(
            LDAP_ADMIN_DN,
            admin_password
        )

        ensure_services_ou(connection)

        service_dn = (
            f"cn={service_name},{LDAP_SERVICES_DN}"
        )

        descriptions = [
            f"ip={ip_address}".encode(),
            f"port={port}".encode()
        ]

        attributes = {
            "objectClass": [b"device"],
            "cn": [service_name.encode()],
            "description": descriptions
        }

        ldif = modlist.addModlist(attributes)

        try:
            connection.add_s(service_dn, ldif)

            print(
                f"Service '{service_name}' registered in LDAP."
            )

        except ldap.ALREADY_EXISTS:
            # If the service already exists, update its IP and port.
            connection.modify_s(
                service_dn,
                [
                    (
                        ldap.MOD_REPLACE,
                        "description",
                        descriptions
                    )
                ]
            )

            print(
                f"Service '{service_name}' updated in LDAP."
            )

    finally:
        connection.unbind_s()


# -------------------- ZEROMQ PUBLISHER --------------------

context = zmq.Context()
socket = context.socket(zmq.PUB)


publisher_type = input(
    "Enter publisher service (TIME / WEATHER / NEWS): "
).upper()


if publisher_type not in ["TIME", "WEATHER", "NEWS"]:
    print("Unknown publisher type.")
    socket.close()
    context.term()
    exit()


serverName = input(
    "Enter server hostname or IP address "
    "(press Enter to bind to 0.0.0.0): "
)

if not serverName:
    serverName = "0.0.0.0"


try:
    serverPort = int(
        input("Enter server port number: ")
    )
except ValueError:
    print("Invalid input. Using default port 15000.")
    serverPort = 15000


address = f"tcp://{serverName}:{serverPort}"

try:
    socket.bind(address)

except zmq.ZMQError as e:
    print(f"Could not bind Publisher: {e}")
    socket.close()
    context.term()
    exit()


# If the Publisher binds to all interfaces, register its real LAN IP.
if serverName == "0.0.0.0":
    service_ip = get_local_ip()
else:
    try:
        service_ip = network_socket.gethostbyname(serverName)
    except network_socket.gaierror:
        service_ip = serverName


print("\nRegistering service in LDAP...")

admin_password = getpass.getpass(
    f"LDAP password for {LDAP_ADMIN_DN}: "
)

try:
    register_service(
        publisher_type,
        service_ip,
        serverPort,
        admin_password
    )

except ldap.INVALID_CREDENTIALS:
    print("LDAP authentication failed.")
    socket.close()
    context.term()
    exit()

except ldap.SERVER_DOWN:
    print(
        "Could not connect to LDAP server. "
        "Check that slapd is running."
    )
    socket.close()
    context.term()
    exit()

except ldap.LDAPError as e:
    print(f"LDAP error: {e}")
    socket.close()
    context.term()
    exit()


print(
    f"\nPublisher '{publisher_type}' running on {address}"
)
print(
    f"LDAP service: {publisher_type} -> "
    f"{service_ip}:{serverPort}"
)
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

        else:  # NEWS

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

        socket.send_string(message)

        print("Sent:", message)


except KeyboardInterrupt:

    print("\nPublisher stopped.")


finally:

    socket.close()
    context.term()
