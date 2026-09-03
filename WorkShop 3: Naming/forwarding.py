locations = {
    "A": "B",
    "B": "C",
    "C": "D",
    "D": "192.168.1.50:5000"
}

def resolve(location):
    hops = 0

    while location in locations:
        print("Following:", location, "->", locations[location])
        location = locations[location]
        hops += 1

    return location, hops


print("Before optimization:")

address, hops = resolve("A")

print("Final address:", address)
print("Number of hops:", hops)


locations["A"] = address


print("\nAfter optimization:")

address2, hops2 = resolve("A")

print("Final address:", address2)
print("Number of hops:", hops2)

print("\nSimulating failure:")

locations = {
    "A": "B",
    "B": "C",
    "C": "D",
    "D": "192.168.1.50:5000"
}

del locations["C"]

address3, hops3 = resolve("A")

print("Final result:", address3)
print("Number of hops:", hops3)