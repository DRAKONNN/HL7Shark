from hl7apy.core import Message
import requests
from datetime import datetime
from urllib.parse import urljoin

def build_hl7_message():
    """Construye un mensaje HL7 ADT^A01 compatible con la API"""
    msg = Message("ADT_A01", version="2.5")
    
    # MSH Segment (Header)
    msg.msh.msh_1 = "|"
    msg.msh.msh_2 = "^~\\&"
    msg.msh.msh_3 = "HL7_SOURCE"
    msg.msh.msh_4 = "FACILITY"
    msg.msh.msh_5 = "OPENEMR"
    msg.msh.msh_6 = "CLINIC"
    msg.msh.msh_7 = datetime.now().strftime('%Y%m%d%H%M%S')
    msg.msh.msh_9 = "ADT^A01"
    msg.msh.msh_10 = "MSG456"
    msg.msh.msh_11 = "P"
    msg.msh.msh_12 = "2.5"
    
    # PID Segment (Patient Identification)
    pid = msg.add_segment("PID")
    pid.pid_1 = "1"
    pid.pid_2 = "PAT789^^^HOSP^MR"
    pid.pid_5 = "SMITH^JANE^MARIE"
    pid.pid_7 = "19851021"
    pid.pid_8 = "F"
    pid.pid_11 = "123 MAIN ST^^BOSTON^MA^02115"
    pid.pid_13 = "(617)555-1234"
    pid.pid_19 = "456-78-9012"

    return msg

def send_hl7_message(host, port):
    """Envía el mensaje HL7 como HTTP POST"""
    msg = build_hl7_message()
    
    # Convertir a formato ER7 y asegurar el formato correcto
    hl7_str = msg.to_er7()
    hl7_str = hl7_str.replace('\n', '\r').replace('\\&', '\\\&')
    
    # Construir URL
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