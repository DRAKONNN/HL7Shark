from hl7apy.core import Message
import requests
from datetime import datetime
from urllib.parse import urljoin

def build_hl7_message():
    """Construye un mensaje HL7 ADT^A01 compatible con la API"""
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
    """Envía el mensaje HL7 como HTTP POST"""
    msg = build_hl7_message()
    
    # Convertir a formato ER7 sin modificar separadores
    hl7_str = msg.to_er7()
    
    # Construir URL
    # Ejecutar "python -m pip install --upgrade urllib3" si da error "Failed to parse: <url>"
    url = urljoin(f"http://{host}:{port}/", "api/hl7") 
    
    headers = {
        'Content-Type': 'text/plain',
        'Accept': 'text/plain'
    }
    
    try:
        print("Mensaje HL7 a enviar:\n", repr(hl7_str))
        response = requests.post(url, data=hl7_str, headers=headers, timeout=10)
        response.raise_for_status()
        print("\n✅ Mensaje enviado correctamente")
        print("Respuesta del servidor:", response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error al enviar mensaje HL7: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print("Detalles del error:")
            print(f"Código de estado: {e.response.status_code}")
            print(f"Respuesta: {e.response.text}")
        raise

if __name__ == "__main__":
    HOST = "192.168.1.98"
    PORT = 5000
    
    print("Enviando mensaje HL7 a la API...")
    try:
        send_hl7_message(HOST, PORT)
    except Exception as e:
        print(f"❌ Fallo: {str(e)}")