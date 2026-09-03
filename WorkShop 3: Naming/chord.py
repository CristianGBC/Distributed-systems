M = 5
RING_SIZE = 2 ** M

nodes = [1, 4, 9, 11, 14, 18, 20, 21, 28]


def successor(key):
    for node in nodes:
        if node >= key:
            return node

    return nodes[0]


for key in [3, 8, 12, 19, 26, 30]:
    print(
        "Key:", key,
        "-> node:", successor(key)
    )

 #--------------------------------------------
def finger_table(node):
    table = []

    for i in range(M):
        start = (node + 2**i) % RING_SIZE
        target = successor(start)

        table.append((i + 1, start, target))

    return table

print("\nFinger table for node 1")

for entry in finger_table(1):
    print(entry)

#-----------------------------------------
#Todos los nodos con sus tablas

"""
print("\nFinger tables for all nodes")

for node in nodes:
    print(f"\nNode {node}")
    print("i\tstart\tsuccessor")

    for i, start, target in finger_table(node):
        print(f"{i}\t{start}\t{target}")

"""
#-------------------------------------------------
def lookup(start_node, key):
    current = start_node
    target = successor(key)
    path = [current]

    while current != target:
        table = finger_table(current)

        next_node = None

        for _, _, finger in reversed(table):
            if current < key:
                if current < finger <= key:
                    next_node = finger
                    break
            else:
                if finger > current or finger <= key:
                    next_node = finger
                    break

        if next_node is None or next_node == current:
            next_node = successor((current + 1) % RING_SIZE)

        current = next_node
        path.append(current)

    return path


print("\nLookup key 26 starting at node 1")

path = lookup(1, 26)

for node in path:
    print("Visited node:", node)

print("Total hops:", len(path) - 1)

#-------------------------------------------------

print("\nLookup key 12 starting at node 28")

path = lookup(28, 12)

for node in path:
    print("Visited node:", node)

print("Total hops:", len(path) - 1)