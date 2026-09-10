import ldap

LDAP_SERVER = "ldap://localhost"

LDAP_USER = "uid=francisco,ou=People,dc=example,dc=com"

LDAP_PASSWORD = "password"

try:

    connection = ldap.initialize(LDAP_SERVER)

    connection.simple_bind_s(
        LDAP_USER,
        LDAP_PASSWORD
    )

    print("Authentication successful!")

except ldap.INVALID_CREDENTIALS:

    print("Authentication failed!")

except Exception as e:

    print(f"Error: {e}")

finally:

    try:
        connection.unbind_s()
    except:
        pass