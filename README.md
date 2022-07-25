# ap1200
A python script implementing AP1200, an asynchronous network-layer protocol for sending and receiving packets over digital radio. Runs on top of AFSK-1200 with ECC provided by afskmodem.py.
## Classes:
### NetworkInterface:
#### Parameters:
> source: (required, str, "12345678") Callsign/ID

> source_port: (required, int, 0-255) Port

#### Functions:
> Packet <- make_packet([Data (bytes, len<=1024)], [Dest ID ("12345678")]): Return a Packet with the specified parameters

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

> str <- get_flag(): Get the Packet's flag byte as bits ("00000000")

> int <- get_length(): Get the length of the data in the Packet (0-65535)

> bytes <- get_data() : Get the Packet's data

> None <- set_source([ID]): Set the Packet's source ID

> None <- set_dest([ID]): Set the Packet's destination ID

> None <- set_port([Port]): Set the Packet's port

> None <- set_flag([Flag]): Set the Packet's flag byte

> None <- set_data([Data]): Set the Packet's data


> bytes <- save(): Save the whole packet as bytes

> Packet <- load([Packet as bytes]): Load a packet stored as bytes into a Packet class

> List(Packet) <- getGroup([Packet]): Returns the packets stored in a GROUP Packet

> None <- set_group_flag(bool)

> None <- set_checksum_flag(bool)

> None <- set_signature_flag(bool)

> None <- set_key_flag(bool)

> None <- set_encoding_flag(bool)

> None <- set_formatting_flag(bool)

> None <- set_encryption_flag(bool)

> None <- set_subheader_flag(bool)

> bool <- get_group_flag()

> bool <- get_checksum_flag()

> bool <- get_signature_flag()

> bool <- get_key_flag()

> bool <- get_encoding_flag()

> bool <- get_formatting_flag()

> bool <- get_encryption_flag()

> bool <- get_subheader_flag()

### FormatUtils:
#### Functions:
> bytes <- encode_id([String]): Encodes an ID to bytes

> string <- decode_id([Bytes]): Decodes an ID from bytes (b'12345678')

> bytes <- int_to_bytes([Int], [Number of bytes])

> int <- bytes_to_int([Bytes])

> bytes <- trim_bytes([Bytes], [Max length])

> int <- bits_to_int([Bits as string])

> string <- int_to_bits([Int (0-255)])
