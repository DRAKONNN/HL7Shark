from fastapi import FastAPI, Request, HTTPException
import mysql.connector
from datetime import datetime
import logging

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
    return name.capitalize() if name else ''

def format_address_component(component: str) -> str:
    return ' '.join(word.capitalize() for word in component.split()) if component else ''

def get_next_pid():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(pid) FROM patient_data")
        result = cursor.fetchone()
        return (result[0] or 0) + 1
    except mysql.connector.Error as e:
        logger.error(f"Error al obtener el siguiente PID: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def insert_openemr_patient(data: dict) -> int:
    try:
        # Asegurar que el PID sea único y no sea 0
        if not data.get('pid') or data['pid'] == 0:
            data['pid'] = get_next_pid()

        # Asegurar campos mínimos
        required_fields = [
            'street', 'city', 'state', 'postal_code', 'country_code',
            'phone_home', 'phone_biz', 'phone_cell'
        ]
        for field in required_fields:
            data.setdefault(field, '')

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
            str(data['pid']),
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

@app.post("/api/fhir")
async def handle_fhir_json(request: Request):
    try:
        json_data = await request.json()
        logger.info(f"FHIR JSON recibido: {json_data}")

        # Mapear los campos desde FHIR-like JSON al formato OpenEMR
        patient = {
            'pid': int(json_data.get('id', 0)),
            'title': json_data.get('title', 'Mr.'),
            'language': json_data.get('communication', {}).get('language', {}).get('text', 'english'),
            'financial': '1',
            'fname': format_name(json_data.get('name', [{}])[0].get('given', [''])[0]),
            'lname': format_name(json_data.get('name', [{}])[0].get('family', '')),
            'mname': '',
            'DOB': datetime.strptime(json_data.get('birthDate', ''), '%Y-%m-%d').date() if json_data.get('birthDate') else None,
            'street': format_address_component(json_data.get('address', [{}])[0].get('line', [''])[0]),
            'city': format_address_component(json_data.get('address', [{}])[0].get('city', '')),
            'state': json_data.get('address', [{}])[0].get('state', '').upper(),
            'postal_code': json_data.get('address', [{}])[0].get('postalCode', ''),
            'country_code': json_data.get('address', [{}])[0].get('country', 'US').upper(),
            'drivers_license': '',
            'ss': json_data.get('identifier', [{}])[0].get('value', ''),
            'phone_home': json_data.get('telecom', [{}])[0].get('value', ''),
            'phone_biz': '',
            'phone_cell': '',
            'status': 'active',
            'sex': json_data.get('gender', 'unknown').capitalize(),
            'email': '',
            'race': 'U',
            'ethnicity': 'Not Hispanic or Latino',
            'pubpid': str(json_data.get('id', '')),
            'hipaa_mail': 'YES',
            'hipaa_voice': 'YES'
        }

        new_pid = insert_openemr_patient(patient)

        return {"message": "Paciente registrado exitosamente", "pid": new_pid}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)