from fastapi import FastAPI, Request, HTTPException
import mysql.connector
from datetime import datetime
import logging
from typing import Dict, Any

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


def insert_openemr_patient(data: Dict[str, Any]) -> int:
    conn = None
    cursor = None
    try:
        # Autoincremented PID
        data['pid'] = get_next_pid()

        # Ensure minimum fields
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
        return data['pid'] # Autoincremented PID

    except mysql.connector.Error as err:
        logger.error(f"Error MySQL: {err}", exc_info=True)
        raise RuntimeError(f"Error de base de datos: {err}")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

def process_fhir_patient(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts FHIR Patient data to OpenEMR format"""
    return {
        'pid': int(patient_data.get('id', 0)),
        'title': 'Mr.' if patient_data.get('gender', '').lower() == 'male' else 'Ms.',
        'language': 'english',
        'financial': '1',
        'fname': format_name(patient_data.get('name', [{}])[0].get('given', [''])[0]),
        'lname': format_name(patient_data.get('name', [{}])[0].get('family', '')),
        'mname': patient_data.get('name', [{}])[0].get('given', ['', ''])[1] if len(patient_data.get('name', [{}])[0].get('given', ['', ''])) > 1 else '',
        'DOB': datetime.strptime(patient_data.get('birthDate', ''), '%Y-%m-%d').date() if patient_data.get('birthDate') else None,
        'street': format_address_component(patient_data.get('address', [{}])[0].get('line', [''])[0]),
        'city': format_address_component(patient_data.get('address', [{}])[0].get('city', '')),
        'state': patient_data.get('address', [{}])[0].get('state', '').upper(),
        'postal_code': patient_data.get('address', [{}])[0].get('postalCode', ''),
        'country_code': patient_data.get('address', [{}])[0].get('country', 'US').upper(),
        'drivers_license': '',
        'ss': next((id['value'] for id in patient_data.get('identifier', []) 
                   if id.get('system', '').endswith('ssn') or id.get('system', '').endswith('mrn')), ''),
        'phone_home': next((tel['value'] for tel in patient_data.get('telecom', []) 
                          if tel.get('system') == 'phone'), ''),
        'phone_biz': '',
        'phone_cell': next((tel['value'] for tel in patient_data.get('telecom', []) 
                           if tel.get('system') == 'phone' and tel != patient_data.get('telecom', [{}])[0]), ''),
        'status': 'active',
        'sex': patient_data.get('gender', 'unknown').capitalize(),
        'email': next((tel['value'] for tel in patient_data.get('telecom', []) 
                     if tel.get('system') == 'email'), ''),
        'race': 'U',
        'ethnicity': 'Not Hispanic or Latino',
        'pubpid': str(patient_data.get('id', '')),
        'hipaa_mail': 'YES',
        'hipaa_voice': 'YES'
    }

@app.post("/api/fhir")
async def handle_fhir_json(request: Request):
    try:
        json_data = await request.json()
        logger.info(f"FHIR JSON recibido: {json_data}")

        # Check if it is a Bundle
        if json_data.get('resourceType') == 'Bundle':
            results = []
            for entry in json_data.get('entry', []):
                resource = entry.get('resource', {})
                if resource.get('resourceType') == 'Patient':
                    patient = process_fhir_patient(resource)
                    new_pid = insert_openemr_patient(patient)
                    results.append({"resourceType": "Patient", "status": "created", "pid": new_pid})
                else:
                    results.append({"resourceType": resource.get('resourceType'), "status": "processed", "message": "Resource not inserted into database"})
            
            return {"message": "Bundle processed", "results": results}
        
        # Si no es un Bundle, asumir que es un Patient individual
        elif json_data.get('resourceType') == 'Patient':
            patient = process_fhir_patient(json_data)
            new_pid = insert_openemr_patient(patient)
            return {"message": "Patient successfully registered", "pid": new_pid}
        
        else:
            raise HTTPException(status_code=400, detail="Only Patient or FHIR Bundles resources are accepted.")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)