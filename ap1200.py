import afskmodem
import os
from datetime import datetime
"""
x-----------------------------------------------------------x
| AP1200 - A simple, reliable amateur packet radio protocol |
| https://github.com/jmeifert/adr-cfs                       |
x-----------------------------------------------------------x
"""
################################################################################ LOGGING
def get_date_and_time(): # Long date and time for logging
        now = datetime.now()
        return now.strftime('%Y-%m-%d %H:%M:%S')

# Logging level (0: INFO, 1: WARN (recommended), 2: ERROR, 3: NONE)
LOG_LEVEL = 0
#
# Should the log output to the console?
LOG_TO_CONSOLE = True
#
# Should the log output to a log file?
LOG_TO_FILE = False
#
# Where to generate logfile if need be
LOG_PATH = "adr-cfs.log"
#
# How the log identifies which module is logging.
LOG_PREFIX = "(ADR-CFS)"

# Initialize log file if needed
if(LOG_TO_FILE):
    try:
        os.remove(LOG_PATH)
    except:
        pass
    with open(LOG_PATH, "w") as f:
        f.write(get_date_and_time() + " [INFO] " + LOG_PREFIX + " Logging initialized.\n")

def log(level: int, data: str):
    if(level >= LOG_LEVEL):
        output = get_date_and_time()
        if(level == 0):
            output += " [INFO] "
        elif(level == 1):
            output += " [WARN] "
        else:
            output += " [ERR!] "
        output += LOG_PREFIX + " "
        output += data
        if(LOG_TO_FILE):
            with open(LOG_PATH, "a") as f:
                f.write(output + "\n")
        if(LOG_TO_CONSOLE):
            print(output)

################################################################################ General utilities
class FormatUtils:
    # Encode an 8-character ID into a list of bytes
    def encode_id(id: str) -> list:
        return '{:<8}'.format(id).encode("ascii")[0:8]
    
    # Decode an 8-character ID into a list of bytes
    def decode_id(id: list) -> str:
        return id.decode("ascii")[0:8]

    # int to n bytes
    def int_to_bytes(data: int, n: int) -> bytes: 
        if(data > (256 ** n) - 1):
            data = (256 ** n) - 1
        if(data < 0):
            data = 0
        return data.to_bytes(n, "big") # network endianness

    # bytes to int
    def bytes_to_int(data: bytes) -> int: 
        return int.from_bytes(data , "big")

    # shorten bytes object to specified length
    def trim_bytes(data, val: bytes) -> bytes: 
        if(len(data) > val):
            return data[0:val]
        else:
            return data

    # convert bits to an integer from 0-255
    def bits_to_int(bData: str) -> int:
        return int(bData[0:8], 2)
    
    # convert an integer from 0-255 to bits
    def int_to_bits(bData: int) -> str:
        return '{0:08b}'.format(bData)
    
################################################################################ Wrapper class for digital radio interface
class RadioInterface: 
    def __init__(self):
        self.receiver = afskmodem.DigitalReceiver(afskmodem.DigitalModulationTypes.afsk1200()) # see AFSKmodem README.md for more info on these
        self.transmitter = afskmodem.DigitalTransmitter(afskmodem.DigitalModulationTypes.afsk1200())
        self.integrity = 1

    def rx(self, timeout=-1): # Listen for and catch a transmission, report bit error rate and return data (bytes)
        rd, te = self.receiver.rx(timeout)
        if(len(rd) > 12): # Only record integrity for transmissions longer than 12 bytes (header is 16 bytes)
            self.integrity = 1 - (te / len(rd))
        return rd

    def tx(self, data: bytes): # Transmit raw data (bytes)
        self.transmitter.tx(data)

    def get_integrity(self) -> float: # Return integrity of the last received transmission
        return self.integrity

################################################################################ Packet structure and operations
class Packet:
    def __init__(self, n_source = "", n_dest = "", n_port = 0, n_data = b''):
        self.src_id = FormatUtils.encode_id(n_source)
        self.dest_id = FormatUtils.encode_id(n_dest)
        self.port = FormatUtils.int_to_bytes(n_port, 1)
        self.flags = FormatUtils.int_to_bytes(0, 1)
        self.data = FormatUtils.trim_bytes(n_data, 1024)
        self.dlen0 = bytes([FormatUtils.int_to_bytes(len(self.data), 2)[0]])
        self.dlen1 = bytes([FormatUtils.int_to_bytes(len(self.data), 2)[1]])
        self.empty = False
    
    # Return TRUE if this Packet is empty.
    def is_empty(self) -> bool:
        return self.empty

    # Set the source address of this Packet
    def set_source(self, data: str):
        self.src_id = FormatUtils.encode_id(str)
        self.empty = False
    
    # Set the destination address of this Packet
    def set_dest(self, data: str):
        self.dest_id = FormatUtils.encode_id(str)
        self.empty = False

    # Set the destination port of this Packet
    def set_port(self, data: int):
        self.port = FormatUtils.int_to_bytes(data, 1)
        self.empty = False    
    
    # Set the flag byte of this Packet
    def set_flag(self, data: str):
        iv = FormatUtils.bits_to_int(data)
        self.flags = FormatUtils.int_to_bytes(iv, 1)
        self.empty = False
    
    # Set the data payload of this Packet
    def set_data(self, data: bytes):
        self.data = FormatUtils.trim_bytes(data, 1024)
        self.dlen0 = bytes([FormatUtils.int_to_bytes(len(self.data), 2)[0]])
        self.dlen1 = bytes([FormatUtils.int_to_bytes(len(self.data), 2)[1]])
        self.empty = False
    
    # Get the source ID of this Packet
    def get_source(self) -> str:
        return FormatUtils.decode_id(self.src_id).rstrip()

    # Get the destination ID of this Packet
    def get_dest(self) -> str:
        return FormatUtils.decode_id(self.dest_id).rstrip()
    
    # Get the source port of this Packet
    def get_port(self) -> int:
        return FormatUtils.bytes_to_int(self.port)

    # Get the flag byte of this Packet
    def get_flags(self) -> str:
        iv = FormatUtils.bytes_to_int(self.flags)
        return FormatUtils.int_to_bits(iv)

    # Get the data payload of this Packet
    def get_data(self) -> bytes:
        return self.data
    
    # Get the data length of this Packet
    def get_length(self) -> int:
        return FormatUtils.bytes_to_int(self.dlen0 + self.dlen1)

    # Get the GROUP flag on this Packet
    def is_group_flag(self) -> bool:
        sf = self.get_flags()
        if(sf[0] == "1"):
            return True
        return False
    
    # Set the GROUP flag on this Packet
    def set_group_flag(self, v: bool):
        f = self.get_flags()
        sf = list(f)
        if(v):
            sf[0] = "1"
        else:
            sf[0] = "0"
        jf = "".join(sf)
        self.set_flag(jf)
    
    # Get the CHECKSUM flag on this Packet
    def is_checksum_flag(self) -> bool:
        sf = self.get_flags()
        if(sf[1] == "1"):
            return True
        return False
    
    # Set the CHECKSUM flag on this Packet
    def set_checksum_flag(self, v: bool):
        f = self.get_flags()
        sf = list(f)
        if(v):
            sf[1] = "1"
        else:
            sf[1] = "0"
        jf = "".join(sf)
        self.set_flag(jf)
    
    # Get the SIGNATURE flag on this Packet
    def is_signature_flag(self) -> bool:
        sf = self.get_flags()
        if(sf[2] == "1"):
            return True
        return False
    
    # Set the SIGNATURE flag on this Packet
    def set_signature_flag(self, v: bool):
        f = self.get_flags()
        sf = list(f)
        if(v):
            sf[2] = "1"
        else:
            sf[2] = "0"
        jf = "".join(sf)
        self.set_flag(jf)
    
    # Get the KEY flag on this Packet
    def is_key_flag(self) -> bool:
        sf = self.get_flags()
        if(sf[3] == "1"):
            return True
        return False
    
    # Set the KEY flag on this Packet
    def set_key_flag(self, v: bool):
        f = self.get_flags()
        sf = list(f)
        if(v):
            sf[3] = "1"
        else:
            sf[3] = "0"
        jf = "".join(sf)
        self.set_flag(jf)

    # Get the ENCODING flag on this Packet
    def is_encoding_flag(self) -> bool:
        sf = self.get_flags()
        if(sf[4] == "1"):
            return True
        return False
    
    # Set the ENCODING flag on this Packet
    def set_encoding_flag(self, v: bool):
        f = self.get_flags()
        sf = list(f)
        if(v):
            sf[4] = "1"
        else:
            sf[4] = "0"
        jf = "".join(sf)
        self.set_flag(jf)
    
    # Get the FORMATTING flag on this Packet
    def is_formatting_flag(self) -> bool:
        sf = self.get_flags()
        if(sf[5] == "1"):
            return True
        return False
    
    # Set the FORMATTING flag on this Packet
    def set_formatting_flag(self, v: bool):
        f = self.get_flags()
        sf = list(f)
        if(v):
            sf[5] = "1"
        else:
            sf[5] = "0"
        jf = "".join(sf)
        self.set_flag(jf)
    
    # Get the ENCRYPTION flag on this Packet
    def is_encryption_flag(self) -> bool:
        sf = self.get_flags()
        if(sf[6] == "1"):
            return True
        return False
    
    # Set the ENCRYPTION flag on this Packet
    def set_encryption_flag(self, v: bool):
        f = self.get_flags()
        sf = list(f)
        if(v):
            sf[6] = "1"
        else:
            sf[6] = "0"
        jf = "".join(sf)
        self.set_flag(jf)

    # Get the SUBHEADER flag on this Packet
    def is_subheader_flag(self) -> bool:
        sf = self.get_flags()
        if(sf[7] == "1"):
            return True
        return False
    
    # Set the SUBHEADER flag on this Packet
    def set_subheader_flag(self, v: bool):
        f = self.get_flags()
        sf = list(f)
        if(v):
            sf[7] = "1"
        else:
            sf[7] = "0"
        jf = "".join(sf)
        self.set_flag(jf)

    # Save the packet to bytes
    def save(self) -> bytes: 
        p = self.src_id
        p += self.dest_id
        p += self.port
        p += self.flags
        p += self.dlen0
        p += self.dlen1
        p += self.data
        return p
    
    # Load a packet from bytes
    def load(self, bdata: bytes): 
        try:
            self.empty = False
            self.src_id = bdata[0:8]
            self.dest_id = bdata[8:16]
            self.port = bdata[16:17]
            self.flags = bdata[17:18]
            self.dlen0 = bdata[18:19]
            self.dlen1 = bdata[19:20]
            dLen = FormatUtils.bytes_to_int(self.dlen0 + self.dlen1)
            self.data = bdata[20:20+dLen]
        except Exception as e:
            self.empty = True
            self.src_id = b'        '
            self.dest_id = b'        '
            self.port = FormatUtils.int_to_bytes(0, 1)
            self.flags = FormatUtils.int_to_bytes(0, 1)
            self.dlen0 = FormatUtils.int_to_bytes(0, 1)
            self.dlen1 = FormatUtils.int_to_bytes(0, 1)
            dLen = 0
            self.data = b''
    
    # Write bytes to build a Packet
    def __write_raw(self, src_id, dest_id, port, flags, dlen0, dlen1, data):
        self.src_id = src_id
        self.dest_id = dest_id
        self.port = port
        self.flags = flags
        self.dlen0 = dlen0
        self.dlen1 = dlen1
        self.data = data
    
    # Extract grouped packets from their container
    def get_grouped_packets(self):
        try:
            if(not self.is_group_flag()):
                return []
            op = []
            n = 0
            pd = self.get_data()
            while(n < len(pd) - 20):
                log(0, "Reading grouped packet at index " + str(n))
                gp = Packet() # instantiate a packet and read into it
                src_id = pd[n:n+8]
                dest_id = pd[n+8:n+16]
                port = pd[n+16:n+17]
                flag = pd[n+17:n+18]
                dlen0 = pd[n+18:n+19]
                dlen1 = pd[n+19:n+20]
                dLen = FormatUtils.bytes_to_int(dlen0 + dlen1)
                if(n+20+dLen > len(pd)): # do not overflow
                    break
                data = pd[n+20:n+20+dLen]
                gp.__write_raw(src_id, dest_id, port, flag, dlen0, dlen1, data)  # write to packet
                op.append(gp) # store packet in array
                n = n + 20 + dLen # next packet
            return(op)
        except:
            log(1, "Failed to extract grouped packets.")
            return []

################################################################################ High-level operations
class NetworkInterface:
    def __init__(self, id: str, port: int):
        self.id = id
        self.port = port
        self.ri = RadioInterface()
        log(0, "Instantiated a NetworkInterface for ID " + self.id + ". (" + str(self.port) + ")")
    
    # Return a Packet with the specified parameters
    def make_packet(self, dest: str, data: bytes) -> Packet:
        return Packet(self.id, dest, self.port, data)
    
    # Send a Packet
    def send_packet(self, p: Packet):
        log(0, "Sending a Packet addressed to " + p.get_dest() + ". (" + str(p.get_port()) + ")")
        self.ri.tx(p.save())
    
    # Listen for and return any Packet
    def listen_for_any_packet(self, timeout=-1) -> Packet: 
        log(0, "Listening for any Packet...")
        while True:
            rd = self.ri.rx(timeout)
            if(rd != b''):
                p = Packet()
                p.load(rd)
                log(0, "Caught a Packet addressed to " + p.get_dest() + ":" + str(p.get_port()) + ".")
                return p
    
    # Listen for and return a Packet addressed to this interface
    def listen_for_packet(self, timeout=-1) -> Packet: 
        log(0, "Listening for a Packet addressed to this NetworkInterface (" + self.id + ":" + str(self.port) + ")...")
        while True:
            rd = self.ri.rx(timeout)
            if(rd != b''):
                p = Packet()
                p.load(rd)
                if(p.get_dest() == self.id and int(p.get_port()) == int(self.port)):
                    log(0, "Received a Packet addressed to this NetworkInterface (" + self.id + ":" + str(self.port) + ").")
                    return p
    
    # Get the integrity of the most recently received Packet
    def get_integrity(self) -> float: 
        return self.ri.get_integrity()
