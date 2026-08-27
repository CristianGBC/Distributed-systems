import zmq
import time
import pickle
import random
import sys


context = zmq.Context()

sender = context.socket(zmq.PUSH)


# ==========================================
# Source ID
# ==========================================

if len(sys.argv) > 1:
    source_id = sys.argv[1]
else:
    source_id = "1"


# ==========================================
# Broker configuration
# ==========================================

brokerName = input(
    "Enter broker hostname or IP address: "
)

if not brokerName:
    brokerName = "localhost"


brokerPort = 13000


address = (
    f"tcp://{brokerName}:{brokerPort}"
)

sender.connect(address)


print(
    f"Source {source_id} connected to "
    f"{address}"
)

print()


# ==========================================
# Generate work
# ==========================================

for i in range(10):

    workload = random.randint(1, 10)

    work = (
        workload,
        i,
        source_id
    )

    print(
        f"Source {source_id} sending:",
        work
    )

    sender.send(
        pickle.dumps(work)
    )

    time.sleep(0.5)


print(
    f"\nSource {source_id} finished."
)


sender.close()
context.term()