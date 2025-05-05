from hl7apy.core import Message
import socket
from datetime import datetime

'''
message = (
    "MSH|^~\&|NYC_Health_ADT||||20080115153000||ADT^A01^ADT_A01|0123456789|P|2.5||||AL"
    "EVN||20080115153000||AAA|AAA|20080114003000"
    "PID|1|123456789^^^HOSP^MR|||RICHARDS^REED^NATHANIEL||19800101|M|||2222 HOME STREET^^ANN ARBOR^MI^12345^USA||555-555-2004\R\444-333-222|||M"
    "NK1|1|RICHARDS^SUE^STORM|SPO|2222 HOME STREET^^ANN ARBOR^MI^^USA"
    "PV1|1|I|ICU^123^B^1||||12345^Smith^Anna^MD"
)
'''

def build_hl7_message(): # Message HL7 v2.5
    msg = Message("ADT_A01", version="2.5")
    
    # MSH Segment (Header)
    msg.msh.msh_3 = 'NYC_Health_ADT' # Good Health Hospital ADT
    msg.msh.msh_7 = '20080115153000'
    msg.msh.msh_9 = 'ADT^A01^ADT_A01'
    msg.msh.msh_10 = "0123456789"
    msg.msh.msh_11 = "P"
    msg.msh.msh_16 = "AL"
        
    # EVN Segment (Event)
    msg.evn.evn_2 = msg.msh.msh_7
    msg.evn.evn_4 = "AAA"
    msg.evn.evn_5 = msg.evn.evn_4
    msg.evn.evn_6 = '20080114003000'

    # PID Segment (Patient Identification)
    pid = msg.add_segment("PID")
    pid.pid_1 = "1"
    pid.pid_2 = "123456789^^^HOSP^MR"
    pid.pid_5 = "RICHARDS^REED^NATHANIEL"
    pid.pid_7 = "19800101"
    pid.pid_8 = "M"
    pid.pid_11 = "42 STREET AND MADISON AVENUE^^NEW YORK^NY^10017^USA"
    pid.pid_11 = "2222 HOME STREET^^ANN ARBOR^MI^12345^USA"
    pid.pid_13 = "555-555-2004~444-333-222"
    pid.pid_16 = "M"

    # NK1 Segment (Next of Kin)
    msg.nk1.nk1_1 = '1'
    msg.nk1.nk1_2 = 'RICHARDS^SUE^STORM'
    msg.nk1.nk1_3 = 'SPO'
    msg.nk1.nk1_4 = '2222 HOME STREET^^ANN ARBOR^MI^^USA'

    # PV1 Segment (Patient Visit)
    pv1 = msg.add_segment("PV1")
    pv1.pv1_1 = "1"
    pv1.pv1_2 = "I"
    pv1.pv1_3 = "ICU^123^B^1"
    pv1.pv1_7 = "12345^Smith^Anna^MD^^^"

    return msg

def send_hl7_message(host, port):
    msg = build_hl7_message()
    hl7_str = msg.to_er7()
    mllp_message = f"\x0b{hl7_str}\x1c\x0d"

    with socket.create_connection((host, port)) as s:
        s.sendall(mllp_message.encode())
        print("HL7 message sent")

        # Wait ACK HL7
        ack_data = ""
        while True:
            data = s.recv(4096).decode()
            if not data:
                break
            ack_data += data
            if '\x1c\x0d' in ack_data:
                break
        ack_clean = ack_data.strip("\x0b").strip("\x1c\x0d")
        print("ACK received:\n", ack_clean)

if __name__ == "__main__":
    HOST = "192.168.1.98" # CHANGE URL WITH YOUR SERVER
    PORT = 5000
    send_hl7_message(HOST, PORT)