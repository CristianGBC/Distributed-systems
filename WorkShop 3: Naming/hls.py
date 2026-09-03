tree = {
    "ROOT": {
        "AMERICA": {
            "ECUADOR": {
                "IBARRA": {},
                "QUITO": {}
            },
            "USA": {}
        },
        "EUROPE": {}
    }
}


entities = {
    "IBARRA": {
        "server01": "10.0.1.20"
    },
    "QUITO": {
        "server02": "10.0.2.30"
    }
}


parents = {
    "IBARRA": "ECUADOR",
    "QUITO": "ECUADOR",
    "ECUADOR": "AMERICA",
    "USA": "AMERICA",
    "AMERICA": "ROOT",
    "EUROPE": "ROOT",
    "ROOT": None
}


def find_entity_domain(entity):
    for domain, domain_entities in entities.items():
        if entity in domain_entities:
            return domain

    return None


def path_to_root(domain):
    path = []

    while domain is not None:
        path.append(domain)
        domain = parents[domain]

    return path


def lookup(entity, starting_domain):
    print(f"\nLooking for {entity} from {starting_domain}")

    target_domain = find_entity_domain(entity)

    # Entity does not exist
    if target_domain is None:
        print(starting_domain)
        print("-> Entity not found")
        return None

    # Entity is in the local domain
    if starting_domain == target_domain:
        print(starting_domain)
        print("->", entity)

        address = entities[target_domain][entity]

        print("Address:", address)

        return address

    # Paths from both domains to ROOT
    start_path = path_to_root(starting_domain)
    target_path = path_to_root(target_domain)

    # Find the closest common ancestor
    common_domain = None

    for domain in start_path:
        if domain in target_path:
            common_domain = domain
            break

    # Move upward
    current = starting_domain

    print(current)

    while current != common_domain:
        current = parents[current]
        print("->", current)

    # Move downward toward the target domain
    common_index = target_path.index(common_domain)

    downward_path = target_path[:common_index]

    for domain in reversed(downward_path):
        print("->", domain)

    print("->", entity)

    address = entities[target_domain][entity]

    print("Address:", address)

    return address


# TEST 1: server01 from IBARRA

lookup("server01", "IBARRA")


# TEST 2: server02 from IBARRA

lookup("server02", "IBARRA")


# TEST 3: server99 from IBARRA

lookup("server99", "IBARRA")


# MOVE server01 FROM IBARRA TO QUITO

print("\nMOVING SERVER01 FROM IBARRA TO QUITO")

entities["IBARRA"].pop("server01")

entities["QUITO"]["server01"] = "10.0.2.40"


# TEST AFTER MOVING server01

lookup("server01", "IBARRA")