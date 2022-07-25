from ap1200 import NetworkInterface

print("AP1200 RX Demo")
print("Homepage: https://github.com/lavajuno/ap1200/")
print("Updates: https://github.com/lavajuno/ap1200/releases")
print("Enter ID to listen on (BLANK:ANY)")
this_addr = input(":")
if(this_addr == ""):
    filterListener = False
    ni = NetworkInterface("        ", 255)
else:
    filterListener = True
    print("Enter port to listen on (0-255)")
    this_port = input(":")
    ni = NetworkInterface(this_addr, this_port)

while(True):
    print("Listening for packet...\n")
    if(filterListener):
        p = ni.listen_for_packet()
    else:
        p = ni.listen_for_any_packet()
    
    # get attributes
    p_source = p.get_source()
    p_dest = p.get_dest()
    p_port = p.get_port()
    p_flag = p.get_flags()
    p_length = p.get_length()
    p_data = p.get_data()
    p_integrity = round(ni.get_integrity() * 100, 4)

    # display attributes
    print("\nPacket received (Integrity: " + str(p_integrity) + "%)")
    if(p_integrity < 70):
        print("WARNING: Low packet integrity. Uncorrectable errors may be present.")
    print(str(p_source) + " -> " + str(p_dest) + " (" + str(p_port)
     + ") [F: " + p_flag + ", L: " + str(p_length) + "]:")

    # handle contents
    if(p.is_group_flag()):
        print("Packet is a group. Showing grouped packets:")
        gp = p.get_grouped_packets()
        # display each packet in group
        for i in gp:
            i_source = i.get_source()
            i_dest = i.get_dest()
            i_port = i.get_port()
            i_flag = i.get_flags()
            i_length = i.get_length()
            i_data = i.get_data()
            print(i_source + " -> " + i_dest + " (" + str(i_port) + ") [F: " + i_flag + ", L: " + str(i_length) + "]:")
            print(i_data.decode("ascii", "ignore"))
    else:
        # if not a group print the packet's data
        print(p_data.decode("ascii", "ignore"))
    
    print("Done. (CTRL-C to exit)")