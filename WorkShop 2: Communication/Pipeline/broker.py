import zmq
import pickle


context = zmq.Context()


# ==========================================
# INPUT: Receive jobs from Sources
# ==========================================

receiver = context.socket(zmq.PULL)

input_port = 13000

receiver.bind(
    f"tcp://*:{input_port}"
)


# ==========================================
# OUTPUT: Send jobs to Workers
# ==========================================

sender = context.socket(zmq.PUSH)

output_port = 14000

sender.bind(
    f"tcp://*:{output_port}"
)


print("Broker started")
print(f"Input port:  {input_port}")
print(f"Output port: {output_port}")
print("Waiting for jobs...\n")


try:

    while True:

        # Receive work from any Source
        data = receiver.recv()

        work = pickle.loads(data)

        print("Broker received:", work)

        # Forward work to one Worker
        sender.send(data)

        print("Broker forwarded:", work)
        print()


except KeyboardInterrupt:

    print("\nBroker stopped.")


finally:

    receiver.close()
    sender.close()
    context.term()