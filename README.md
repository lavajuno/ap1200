# ap1200
A python script implementing AP1200, an asynchronous network-layer protocol for sending and receiving packets over digital radio. Runs on top of AFSK-1200 with ECC provided by afskmodem.py.
## Classes:
### NetworkInterface:
#### Parameters:
> source: (required, str, "12345678") Callsign/ID

> source_port: (required, int, 0-255) Port

#### Functions:
> Packet <- make_packet(bytes, str): Return a Packet with the specified parameters (Packet's data and destination ID)

> None <- send_packet([Packet]): Sends a Packet

> Packet <- listen_for_any_packet([Timeout (seconds)]): Listens for any Packet

> Packet <- listen_for_packet([Timeout (seconds)]): Listens for a Packet addressed to this NetworkInterface

> float <- get_integrity(): Get the data integrity of the last received Packet

### Packet:
#### Parameters:
> src_id: (required, str, "12345678") Source address

> dest_id: (required, str, "12345678") Destination address

> port: (optional, int, 0-255, default:0) Port

> data: (optional, bytes, len<=1024, default:b'') Data to transmit

#### Functions:
> str <- get_source(): Get the Packet's source ID ("12345678")

> str <- get_dest(): Get the Packet's destination ID ("12345678")

> int <- get_port(): Get the Packet's port (0-255)

> int <- get_flag(): Get the packet's flag

> int <- get_length(): Get the length of the data in the Packet (0-65535)

> bytes <- get_data() : Get the Packet's data

> None <- set_source(str): Set the Packet's source ID "12345678"

> None <- set_dest(str): Set the Packet's destination ID "12345678"

> None <- set_port(int): Set the Packet's port (0-255)

> None <- set_flag(int): Set the packet's flag (0-255)

> bytes <- save(): Save the whole packet as bytes

> Packet <- load(bytes): Load a packet stored as bytes into a Packet class




