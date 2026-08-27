import zmq
import time
import pickle
import sys


context = zmq.Context()

receiver = context.socket(zmq.PULL)


# ==========================================
# Worker ID
# ==========================================

if len(sys.argv) > 1:
    worker_id = sys.argv[1]
else:
    worker_id = "1"


# ==========================================
# Broker
# ==========================================

brokerName = input(
    "Enter broker hostname or IP address: "
)

if not brokerName:
    brokerName = "localhost"


brokerPort = 14000


address = (
    f"tcp://{brokerName}:{brokerPort}"
)

receiver.connect(address)


print(
    f"Worker {worker_id} connected to "
    f"{address}"
)

print("Waiting for jobs...\n")


# ==========================================
# Process jobs
# ==========================================

try:

    while True:

        data = receiver.recv()

        work = pickle.loads(data)


        workload = work[0]
        job_id = work[1]
        source_id = work[2]


        print(
            f"Worker {worker_id} received:"
        )

        print(
            f"  Source: {source_id}"
        )

        print(
            f"  Job: {job_id}"
        )

        print(
            f"  Workload: {workload}"
        )


        # Simulate processing
        time.sleep(
            workload * 0.1
        )


        print(
            f"Worker {worker_id} "
            f"finished job {job_id}\n"
        )


except KeyboardInterrupt:

    print(
        f"\nWorker {worker_id} stopped."
    )


finally:

    receiver.close()
    context.term()