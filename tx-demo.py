from ap1200 import NetworkInterface

print("ap1200 TX Demo")
print("Homepage: https://github.com/lavajuno/ap1200/")
print("Updates: https://github.com/lavajuno/ap1200/releases")
print("Enter source callsign/ID")
source_addr = input(":")
print("Enter source port (0-255)")
port = int(input(":"))
ni = NetworkInterface(source_addr, port)
while True:
    print("Enter message string (ASCII):")
    user_message = input()
    print("Enter dest callsign/ID")
    dest_id = input(":")
    encoded_message = user_message.encode("ascii", "ignore")
    print("Transmitting...")
    p = ni.make_packet(dest_id, encoded_message)
    ni.send_packet(p)
    print("Done. (CTRL-C to exit)\n")
