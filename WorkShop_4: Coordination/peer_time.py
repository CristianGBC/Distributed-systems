import zmq
import threading
import time
import random


# Peer configuration

peer_id = input("Enter peer ID [1]: ").strip()

if not peer_id:
    peer_id = "1"


port_input = input(
    "Enter listening port [6001]: "
).strip()

if not port_input:
    port = 6001
else:
    try:
        port = int(port_input)

        if port < 1 or port > 65535:
            print(
                "Invalid port. Using default port 6001."
            )
            port = 6001

    except ValueError:
        print(
            "Invalid port. Using default port 6001."
        )
        port = 6001



# Simulated local clock

clock_offset = random.randint(-5, 5)


def get_local_time():
    return time.time() + clock_offset

# ==========================================
# Peer listener
# ==========================================

def peer_listener():

    context = zmq.Context()
    socket = context.socket(zmq.REP)

    try:
        address = f"tcp://*:{port}"
        socket.bind(address)

        print(
            f"Peer {peer_id} listening on port {port}..."
        )

        while True:

            # Wait for a request from another peer
            message = socket.recv_string()

            print(
                f"Peer {peer_id} received: {message}"
            )

            if message == "TIME_REQUEST":

                local_time = get_local_time()

                socket.send_string(
                    str(local_time)
                )

            else:
                socket.send_string(
                    "UNKNOWN_REQUEST"
                )

    except zmq.ZMQError as e:
        print(
            f"Peer {peer_id} ZeroMQ error: {e}"
        )

    except Exception as e:
        print(
            f"Peer {peer_id} unexpected error: {e}"
        )

    finally:
        socket.close()
        context.term()


#-----------------------------------------------------------------------------
# Request time from another peer


def request_peer_time(host, peer_port):

    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    socket.setsockopt(zmq.RCVTIMEO, 3000)
    socket.setsockopt(zmq.SNDTIMEO, 3000)
    socket.setsockopt(zmq.LINGER, 0)

    try:
        address = f"tcp://{host}:{peer_port}"

        print(
            f"Peer {peer_id} requesting time from "
            f"{address}"
        )

        socket.connect(address)

        # Send time request
        socket.send_string("TIME_REQUEST")

        # Receive peer time
        response = socket.recv_string()

        peer_time = float(response)

        print(
            f"Received time from {address}: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(peer_time))}"
        )

        return peer_time

    except zmq.Again:
        print(
            f"Peer at {host}:{peer_port} "
            f"did not respond."
        )
        return None

    except zmq.ZMQError as e:
        print(f"ZeroMQ error: {e}")
        return None

    except ValueError:
        print("Invalid time received from peer.")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

    finally:
        socket.close()
        context.term()

#-----------------------------------------------------------------------------
peers = {
    "1": ("localhost", 6001),
    "2": ("localhost", 6002),
    "3": ("localhost", 6003),
}

K = 3
CYCLE_INTERVAL = 5

def add_random_drift():
    global clock_offset

    drift = random.randint(-5, 5)

    clock_offset += drift

    print(
        f"\n*** Random clock drift applied: "
        f"{drift:+d} seconds ***"
    )

    print(
        f"New clock offset: "
        f"{clock_offset:.3f} seconds"
    )


# Synchronization cycle
def synchronize():
    global clock_offset

    print(
        f"\n--- Peer {peer_id} synchronization ---"
    )

    # Get this peer's current local time
    local_time = get_local_time()

    collected_times = [local_time]

    print(
        f"Peer {peer_id} local time: "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(local_time))}"
    )

    # Request time from all other peers
    for other_id, (host, peer_port) in peers.items():

        if other_id == peer_id:
            continue

        peer_time = request_peer_time(
            host,
            peer_port
        )

        if peer_time is not None:
            collected_times.append(peer_time)

    # Calculate average time
    average_time = sum(collected_times) / len(collected_times)

    # Calculate adjustment
    adjustment = average_time - local_time

    # Adjust simulated local clock
    clock_offset += adjustment

    print(
        f"\nAverage time: "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(average_time))}"
    )

    print(
        f"Clock adjustment: {adjustment:.3f} seconds"
    )

    adjusted_time = get_local_time()

    print(
        f"Peer {peer_id} adjusted time: "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(adjusted_time))}"
    )





if __name__ == "__main__":

    print(f"\nPeer ID: {peer_id}")
    print(f"Listening port: {port}")
    print(
        f"Initial clock drift: "
        f"{clock_offset} seconds"
    )

    local_time = get_local_time()

    print(
        "Local simulated time:",
        time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(local_time)
        )
    )

    # Start listener in a separate thread
    listener_thread = threading.Thread(
        target=peer_listener,
        daemon=True
    )

    listener_thread.start()

    # Give all peers time to start
    time.sleep(5)

    cycle = 1

    try:

        while True:

            print(
                f"\n================================"
            )

            print(
                f"PEER {peer_id} - CYCLE {cycle}"
            )

            print(
                f"================================"
            )

            # Add random drift every K cycles
            if cycle % K == 0:
                add_random_drift()

            # Synchronize with other peers
            synchronize()

            cycle += 1

            time.sleep(CYCLE_INTERVAL)

    except KeyboardInterrupt:

        print(
            f"\nPeer {peer_id} stopped."
        )