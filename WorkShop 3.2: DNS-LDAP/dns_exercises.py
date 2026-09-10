import dns.resolver
import dns.reversename
import dns.query
import dns.message
import dns.rdatatype


# B1 - Basic Domain Lookup

def b1_basic_lookup():
    print("\n=== B1: Basic Domain Lookup ===")

    domain = "yachaytech.edu.ec"

    try:
        answers = dns.resolver.resolve(domain, "A")

        for answer in answers:
            print(f"{domain} -> {answer}")

    except Exception as e:
        print(f"Error: {e}")


# B2 - Reverse Lookup

def b2_reverse_lookup():
    print("\n=== B2: Reverse Lookup ===")

    ip = "8.8.8.8"

    try:
        reverse_name = dns.reversename.from_address(ip)
        answers = dns.resolver.resolve(reverse_name, "PTR")

        for answer in answers:
            print(f"{ip} -> {answer}")

    except Exception as e:
        print(f"Error: {e}")


# B3 - Query Specific DNS Server

def b3_specific_dns_server():
    print("\n=== B3: Query Specific DNS Server ===")

    domain = "hpc.cedia.edu.ec"

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["1.1.1.1"]

    try:
        answers = resolver.resolve(domain, "A")

        print("DNS Server: 1.1.1.1")

        for answer in answers:
            print(f"{domain} -> {answer}")

    except Exception as e:
        print(f"Error: {e}")


# B4 - MX Records

def b4_mx_records():
    print("\n=== B4: MX Records ===")

    domain = "yachaytech.edu.ec"

    try:
        answers = dns.resolver.resolve(domain, "MX")

        for answer in answers:
            print(
                f"Priority: {answer.preference}, "
                f"Mail Server: {answer.exchange}"
            )

    except Exception as e:
        print(f"Error: {e}")


# B5 - NS Records

def b5_ns_records():
    print("\n=== B5: NS Records ===")

    domain = "yachaytech.edu.ec"

    try:
        answers = dns.resolver.resolve(domain, "NS")

        for answer in answers:
            print(f"Name Server: {answer}")

    except Exception as e:
        print(f"Error: {e}")


# B6 - SOA Record

def b6_soa_record():
    print("\n=== B6: SOA Record ===")

    domain = "yachaytech.edu.ec"

    try:
        answers = dns.resolver.resolve(domain, "SOA")

        for answer in answers:
            print(f"Primary server: {answer.mname}")
            print(f"Responsible mailbox: {answer.rname}")
            print(f"Serial: {answer.serial}")
            print(f"Refresh: {answer.refresh}")
            print(f"Retry: {answer.retry}")
            print(f"Expire: {answer.expire}")
            print(f"Minimum: {answer.minimum}")

    except Exception as e:
        print(f"Error: {e}")


# B7 - CNAME Record

def b7_cname_record():
    print("\n=== B7: CNAME Record ===")

    domain = "www.microsoft.com"

    try:
        answers = dns.resolver.resolve(domain, "CNAME")

        for answer in answers:
            print(f"{domain} -> {answer}")

    except dns.resolver.NoAnswer:
        print(f"No CNAME record was found for {domain}.")

    except Exception as e:
        print(f"Error: {e}")


# B8 - Detailed DNS Query

def b8_debug_query():
    print("\n=== B8: Detailed DNS Query ===")

    domain = "yachaytech.edu.ec"

    try:
        query = dns.message.make_query(
            domain,
            dns.rdatatype.A
        )

        response = dns.query.udp(
            query,
            "8.8.8.8",
            timeout=5
        )

        print("\n--- QUESTION SECTION ---")
        for item in response.question:
            print(item)

        print("\n--- ANSWER SECTION ---")
        for item in response.answer:
            print(item)

        print("\n--- AUTHORITY SECTION ---")
        for item in response.authority:
            print(item)

        print("\n--- ADDITIONAL SECTION ---")
        for item in response.additional:
            print(item)

    except Exception as e:
        print(f"Error: {e}")


# B9 - Non-Existent Domain

def b9_nonexistent_domain():
    print("\n=== B9: Non-Existent Domain ===")

    domain = "nonexistdomain12345.com"

    try:
        answers = dns.resolver.resolve(domain, "A")

        for answer in answers:
            print(answer)

    except dns.resolver.NXDOMAIN:
        print(
            f"NXDOMAIN: The domain {domain} does not exist."
        )

    except Exception as e:
        print(f"Error: {e}")


# Main

def main():
    b1_basic_lookup()
    b2_reverse_lookup()
    b3_specific_dns_server()
    b4_mx_records()
    b5_ns_records()
    b6_soa_record()
    b7_cname_record()
    b8_debug_query()
    b9_nonexistent_domain()


if __name__ == "__main__":
    main()