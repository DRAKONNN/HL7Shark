from fastapi import FastAPI, Request, HTTPException, Response
import mysql.connector
from hl7apy.parser import parse_message
from datetime import datetime
import logging
import re

app = FastAPI()

# Configuración de OpenEMR
db_config = {
    'host': 'localhost',
    'user': 'openemr',
    'password': 'openemr',
    'database': 'openemr'
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_hl7_message(hl7_message: str) -> dict:
    """Versión robusta con todos los campos requeridos"""
    try:
        msg = parse_message(hl7_message.replace('\n', '\r'))
        
        # Función helper para manejar campos opcionales
        def get_hl7_value(field, subcomponent=0, default=''):
            try:
                if subcomponent > 0:
                    return field[subcomponent-1].value if len(field) >= subcomponent else default
                return field.value if field else default
            except:
                return default

        # Extracción de PID (versión numérica)
        raw_pid = get_hl7_value(msg.pid.pid_2, 0, '0')
        numeric_pid = int(''.join(filter(str.isdigit, raw_pid))) if raw_pid else 0

        # Dirección (PID-11)
        pid11 = msg.pid.pid_11 if msg.pid.pid_11 else None
        address_components = {
            'street': get_hl7_value(pid11, 1) if pid11 else '',
            'city': get_hl7_value(pid11, 3) if pid11 else '',
            'state': get_hl7_value(pid11, 4) if pid11 else '',
            'postal_code': get_hl7_value(pid11, 5) if pid11 else ''
        }

        return {
            'pid': numeric_pid,
            'title': 'Mr.',  # Valor por defecto
            'language': 'english',
            'financial': '1',
            'fname': get_hl7_value(msg.pid.pid_5, 2) if msg.pid.pid_5 else '',
            'lname': get_hl7_value(msg.pid.pid_5, 1) if msg.pid.pid_5 else '',
            'mname': get_hl7_value(msg.pid.pid_5, 3) if msg.pid.pid_5 else '',
            'DOB': datetime.strptime(get_hl7_value(msg.pid.pid_7), '%Y%m%d').date() if get_hl7_value(msg.pid.pid_7) else None,
            **address_components,  # Desempaqueta los componentes de dirección
            'country_code': 'US',
            'drivers_license': '',
            'ss': get_hl7_value(msg.pid.pid_19),
            'phone_home': re.sub(r'[^\d+]', '', get_hl7_value(msg.pid.pid_13, 1)),
            'phone_biz': '',
            'phone_cell': '',
            'status': 'active',
            'sex': get_hl7_value(msg.pid.pid_8, 0, 'U').upper()[:1],  # M/F/U
            'email': '',
            'race': 'U',  # Desconocido
            'ethnicity': 'Not Hispanic or Latino',
            'pubpid': str(numeric_pid),  # Versión string del PID
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
    """Versión con valores por defecto para todos los campos"""
    try:
        # Aseguramos que todos los campos requeridos existan
        required_fields = [
            'street', 'city', 'state', 'postal_code',
            'phone_home', 'phone_biz', 'phone_cell'
        ]
        
        for field in required_fields:
            data.setdefault(field, '')  # Asigna string vacío si no existe

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO `patient_data` (
            `pid`, `title`, `language`, `financial`, `fname`, `lname`, `mname`, `DOB`,
            `street`, `postal_code`, `city`, `state`, `country_code`,
            `drivers_license`, `ss`, `phone_home`, `phone_biz`, `phone_cell`,
            `status`, `sex`, `email`, `race`, `ethnicity`, `pubpid`,
            `hipaa_mail`, `hipaa_voice`, `regdate`
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