from http import server
import socket

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 1234
    addr = (host, port)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print ("Funcionalitys in this SNMP-Agent:")
    print ("- get <oid>")
    print ("- get-next <oid>")
    print ("- get-bulk <oid>")
    print ("- set <oid> <value>")
    print ("- exit")
    print ("---------------------------------")

    community_str = input("Enter Community String: ")

    while True:
        data = input("Enter Command: ")

        if data == "exit":
            data = data.encode("utf-8")
            client.sendto(data, addr)
            print("Disconnected from the Server.")
            break

        data = community_str + " " + data
        data = data.encode("utf-8")
        client.sendto(data, addr)

        data, addr = client.recvfrom(1024)
        data = data.decode("utf-8")

        print(f"Agent: {data}")

    client.close()
