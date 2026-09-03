import uuid
import socket

entity_id = uuid.uuid5(uuid.NAMESPACE_DNS, "student-Barba")

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

entity = {
    "id": str(entity_id),
    "address": (ip, 5000)
}

print("ORIGINAL ENTITY")
print("Identifier:", entity["id"])
print("Address:", entity["address"])

entity["address"] = (ip, 6000)

print("\nADDRESS CHANGE")
print("Identifier:", entity["id"])
print("Address:", entity["address"])