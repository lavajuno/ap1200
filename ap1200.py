import afskmodem
import os
from datetime import datetime
"""
x-----------------------------------------------------------x
| AP1200 - A simple, reliable amateur packet radio protocol |
| https://github.com/lavajuno/ap1200                        |
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
LOG_PATH = "ap1200.log"
#
# How the log identifies which module is logging.
LOG_PREFIX = "(AP1200)"

# Initialize log file if needed
if(LOG_TO_FILE):
    try:
        os.remove(LOG_PATH)
    except:
        pass
    with open(LOG_PATH, "w") as f:
        f.write(get_date_and_time() + " [  OK  ] " + LOG_PREFIX + " Logging initialized.\n")

def log(level: int, data: str):
    if(level >= LOG_LEVEL):
        output = get_date_and_time()
        if(level == 0):
            output += " [  OK  ] "
        elif(level == 1):
            output += " [ WARN ] "
        else:
            output += " [ERROR!] "
        output += LOG_PREFIX + " "
        output += data
        if(LOG_TO_FILE):
            with open(LOG_PATH, "a") as f:
                f.write(output + "\n")
        if(LOG_TO_CONSOLE):
            print(output)

################################################################################ General utilities
class FormatUtils:
    # Encode an 8-character ID into bytes
    def encode_id(id: str) -> bytes:
        return '{:<8}'.format(id).encode("ascii")[0:8]
    
    # Decode an 8-character ID into bytes
    def decode_id(id: bytes) -> str:
        return id.decode("ascii")[0:8].rstrip()

    # int to n bytes
    def int_to_bytes(data: int, n: int) -> bytes: 
        if(data > (256 ** n) - 1):
            data = (256 ** n) - 1
        if(data < 0):
            data = 0
        return data.to_bytes(n, "big")

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

    def rx(self, timeout=-1) -> bytes: # Listen for and catch a transmission, report bit error rate and return data (bytes)
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
        self.flag = FormatUtils.int_to_bytes(0, 1)
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
    def set_flag(self, data: int):
        self.flag = FormatUtils.int_to_bytes(data, 1)
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
    def get_flag(self) -> int:
        return FormatUtils.bytes_to_int(self.flag)

    # Get the data payload of this Packet
    def get_data(self) -> bytes:
        return self.data
    
    # Get the data length of this Packet
    def get_length(self) -> int:
        return FormatUtils.bytes_to_int(self.dlen0 + self.dlen1)

    # Save the packet to bytes
    def save(self) -> bytes: 
        p = self.src_id
        p += self.dest_id
        p += self.port
        p += self.flag
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
            self.flag = bdata[17:18]
            self.dlen0 = bdata[18:19]
            self.dlen1 = bdata[19:20]
            dLen = FormatUtils.bytes_to_int(self.dlen0 + self.dlen1)
            self.data = bdata[20:20+dLen]
        except Exception as e:
            self.empty = True
            self.src_id = b'        '
            self.dest_id = b'        '
            self.port = FormatUtils.int_to_bytes(0, 1)
            self.flag = FormatUtils.int_to_bytes(0, 1)
            self.dlen0 = FormatUtils.int_to_bytes(0, 1)
            self.dlen1 = FormatUtils.int_to_bytes(0, 1)
            dLen = 0
            self.data = b''

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
