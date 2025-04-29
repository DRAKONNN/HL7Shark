from fastapi import FastAPI, Request, HTTPException, Response
import mysql.connector
from hl7apy.parser import parse_message
from datetime import datetime
import logging
import re

app = FastAPI()

# OpenEMR database configuration
db_config = {
    'host': 'localhost',
    'user': 'openemr',
    'password': 'openemr',
    'database': 'openemr'
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_name(name: str) -> str:
    """Capitalize a name correctly (ex: 'REED' -> 'Reed')"""
    return name.capitalize() if name else ''

def format_address_component(component: str) -> str:
    """Format address components by capitalizing correctly (ex: 'ANN ARBOR' -> 'Ann Arbor')"""
    if not component:
        return ''
    return ' '.join(word.capitalize() for word in component.split())

def parse_hl7_message(hl7_message: str) -> dict:
    """Parsing all required fields"""
    try:
        msg = parse_message(hl7_message.replace('\n', '\r'))
        
        # Helper function to handle optional fields
        def get_hl7_value(field, subcomponent=0, default=''):
            try:
                if subcomponent > 0:
                    return field[subcomponent-1].value if len(field) >= subcomponent else default
                return field.value if field else default
            except:
                return default

        # PID Extraction (Numeric Version)
        raw_pid = get_hl7_value(msg.pid.pid_2, 0, '0')
        numeric_pid = int(''.join(filter(str.isdigit, raw_pid))) if raw_pid else 0

        # Data processing: names (PID-5)
        pid5 = msg.pid.pid_5 if msg.pid.pid_5 else None
        if pid5:
            full_name = pid5.value if pid5 else ''
            name_parts = full_name.split('^')
            
            lname = format_name(name_parts[0]) if len(name_parts) > 0 else ''
            fname = format_name(name_parts[1]) if len(name_parts) > 1 else ''
            mname = format_name(name_parts[2]) if len(name_parts) > 2 else ''
        else:
            lname, fname, mname = '', '', ''

        # Data processing: gender (PID-8)
        pid8 = get_hl7_value(msg.pid.pid_8)if msg.pid.pid_8 else None
        gender = 'Unknown'
        if pid8:
            if pid8 == 'M':
                gender = 'Male'
            if pid8 == 'F':
                gender = 'Female'

        # Data processing: address (PID-11) - Example: "2222 HOME STREET^^ANN ARBOR^MI^12345^US"
        pid11 = msg.pid.pid_11 if msg.pid.pid_11 else None
        if pid11:
            full_address = pid11.value if pid11 else ''
            address_parts = full_address.split('^')
            
            street = format_address_component(address_parts[0]) if len(address_parts) > 0 else ''
            city = format_address_component(address_parts[2]) if len(address_parts) > 2 else ''
            state = address_parts[3].upper() if len(address_parts) > 3 else ''  # Capital letters
            postal_code = address_parts[4] if len(address_parts) > 4 else ''
            country = address_parts[5].upper() if len(address_parts) > 5 else 'XX'
        else:
            street, city, state, postal_code, country = '', '', '', '', 'XX'

        return {
            'pid': numeric_pid,
            'title': 'Mr.',  # Default value
            'language': 'english',
            'financial': '1',
            'fname': fname,
            'lname': lname,
            'mname': mname,
            'DOB': datetime.strptime(get_hl7_value(msg.pid.pid_7), '%Y%m%d').date() if get_hl7_value(msg.pid.pid_7) else None,
            'street': street,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'country_code': country,
            'drivers_license': '',
            'ss': get_hl7_value(msg.pid.pid_19),
            'phone_home': get_hl7_value(msg.pid.pid_13),
            'phone_biz': '',
            'phone_cell': '',
            'status': 'active',
            'sex': gender,
            'email': '',
            'race': 'U',  # Unknown
            'ethnicity': 'Not Hispanic or Latino',
            'pubpid': str(numeric_pid),  # String version of the PID
            'hipaa_mail': 'YES',
            'hipaa_voice': 'YES'
        }

    except ValueError as e:
        logger.error(f"Error en formato de fecha: {str(e)}")
        raise ValueError("Formato de fecha inválido en HL7 (debe ser YYYYMMDD)")
    except Exception as e:
        logger.error(f"Error inesperado al parsear HL7: {str(e)}", exc_info=True)
        raise ValueError(f"Error procesando mensaje HL7: {str(e)}")

def insert_openemr_patient(data: dict) -> int:
    """Version with default values for all fields"""
    try:
        # Ensures that all required fields exist
        required_fields = [
            'street', 'city', 'state', 'postal_code', 'country_code',
            'phone_home', 'phone_biz', 'phone_cell'
        ]
        
        for field in required_fields:
            data.setdefault(field, '')  # Assigns empty string if it does not exist

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO patient_data (
            pid, title, language, financial, fname, lname, mname, DOB,
            street, postal_code, city, state, country_code,
            drivers_license, ss, phone_home, phone_biz, phone_cell,
            status, sex, email, race, ethnicity, pubpid,
            hipaa_mail, hipaa_voice, regdate
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, NOW()
        )
        """

        values = (
            data['pid'],
            data.get('title', ''),
            data.get('language', 'english'),
            data.get('financial', '1'),
            data.get('fname', ''),
            data.get('lname', ''),
            data.get('mname', ''),
            data.get('DOB'),
            data.get('street', ''),
            data.get('postal_code', ''),
            data.get('city', ''),
            data.get('state', ''),
            data.get('country_code', 'US'),
            data.get('drivers_license', ''),
            data.get('ss', ''),
            data.get('phone_home', ''),
            data.get('phone_biz', ''),
            data.get('phone_cell', ''),
            data.get('status', 'active'),
            data.get('sex', 'U'),
            data.get('email', ''),
            data.get('race', ''),
            data.get('ethnicity', ''),
            data.get('pubpid', ''),
            data.get('hipaa_mail', 'YES'),
            data.get('hipaa_voice', 'YES')
        )

        cursor.execute(query, values)
        conn.commit()
        return cursor.lastrowid

    except mysql.connector.Error as err:
        logger.error(f"Error MySQL: {err}", exc_info=True)
        raise RuntimeError(f"Error de base de datos: {err}")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.post("/api/hl7")
async def handle_hl7(request: Request):
    try:
        hl7_data = (await request.body()).decode('utf-8')
        logger.info(f"HL7 recibido:\n{hl7_data}")
        
        patient = parse_hl7_message(hl7_data)
        new_pid = insert_openemr_patient(patient)
        
        ack = f"""MSH|^~\&|API|OPENEMR|CLIENT|FACILITY|{datetime.now().strftime('%Y%m%d%H%M%S')}||ACK^A01|{new_pid}|P|2.5\r
MSA|AA|{new_pid}|Registro exitoso"""
        
        return Response(content=ack, media_type="text/plain")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)