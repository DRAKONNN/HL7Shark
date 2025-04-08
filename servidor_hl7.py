from hl7apy.core import Message
from hl7apy.parser import parse_message
import socket

def receive_mllp_message(conn):
    buffer = ""
    while True:
        data = conn.recv(4096).decode()
        if not data:
            break
        buffer += data
        if '\x1c\x0d' in buffer:
            break
    start = buffer.find('\x0b') + 1
    end = buffer.find('\x1c')
    return buffer[start:end]

def decode_hl7_message(con):
    msg = parse_message(hl7_data, find_groups=False) # parse with hl7apy and display each segment
    # Showing only the segments that the message contains
    print("--------------")
    print("HL7 message:")
    if hasattr(msg, 'msh'):
        print(msg.msh.value)
    if hasattr(msg, 'evn'):
        print(msg.evn.value)
    if hasattr(msg, 'pid'):
        print(msg.pid.value)
    if hasattr(msg, 'nk1'):
        print(msg.nk1.value)
    if hasattr(msg, 'pv1'):
        print(msg.pv1.value)

    print("--------------")
    print("Patient data:")

    print(f"Hospital: {msg.msh.msh_3.value}")

    patient_id = msg.pid.pid_2.value.split("^")[0]
    print(f"Patient ID: {patient_id}")

    last_name, first_name, middle_name = msg.pid.pid_5.value.split("^")
    print(f"Patient name: {first_name} {middle_name} {last_name}")

    print(f"Gender: {msg.pid.pid_8.value}")

    address = msg.pid.pid_11.value.split("^")

    street      = address[0]
    city        = address[2]
    state       = address[3]
    postal_code = address[4]
    country     = address[5]

    full_address = f"{street}, {city}, {state} {postal_code}, {country}"
    print(f"Address: {full_address}")

    nk_last_name, nk_first_name, nk_middle_name = msg.nk1.nk1_2.value.split("^")
    print(f"Next of Kin: {nk_first_name} {nk_middle_name} {nk_last_name}")

def build_ack(hl7_message_str):
    original = parse_message(hl7_message_str, find_groups=False)
    ack = Message("ACK", version="2.5")

    ack.msh.msh_3 = original.msh.msh_5.value
    ack.msh.msh_5 = original.msh.msh_3.value
    ack.msh.msh_7 = original.msh.msh_7.value
    ack.msh.msh_9 = "ACK"
    ack.msh.msh_10 = "ACK12345"
    ack.msh.msh_11 = "P"
    ack.msh.msh_12 = "2.5"

    ack.msa.msa_1 = "AA"
    ack.msa.msa_2 = original.msh.msh_10.value

    return ack.to_er7()

# ---- MAIN LOOP ----
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen(1)
print("HL7 server listening...")

conn, addr = server.accept()
print(f"Connection from {addr}")
hl7_data = receive_mllp_message(conn) # Receiving from MLLP

decode_hl7_message(hl7_data) # Decoding HL7 message

ack = build_ack(hl7_data)
mllp_ack = f"\x0b{ack}\x1c\x0d"
conn.sendall(mllp_ack.encode())
print("--------------")
print("ACK sent.\n")
conn.close()
