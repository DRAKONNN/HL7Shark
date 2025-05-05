import json
import requests
from datetime import datetime

def build_fhir_bundle():
    now_iso = datetime.utcnow().isoformat()

    patient = {
        "resourceType": "Patient",
        "id": "81",
        "identifier": [
            {
                "system": "http://hospital.smarthealth.org/mrn",
                "value": "123456789"
            }
        ],
        "name": [
            {
                "family": "Richards",
                "given": ["Reed", "Nathaniel"]
            }
        ],
        "gender": "male",
        "birthDate": "1980-01-01",
        "address": [
            {
                "line": ["2222 HOME STREET"],
                "city": "ANN ARBOR",
                "state": "MI",
                "postalCode": "12345",
                "country": "USA"
            }
        ],
        "telecom": [
            {"system": "phone", "value": "555-555-2004"},
            {"system": "phone", "value": "444-333-222"}
        ],
        "maritalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                "code": "M"
            }]
        }
    }

    related_person = {
        "resourceType": "RelatedPerson",
        "id": "related-1",
        "patient": {"reference": "Patient/123456789"},
        "name": {
            "family": "Richards",
            "given": ["Sue", "Storm"]
        },
        "relationship": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                "code": "SPO",
                "display": "Spouse"
            }]
        }],
        "address": {
            "line": ["2222 HOME STREET"],
            "city": "ANN ARBOR",
            "state": "MI",
            "country": "USA"
        }
    }

    encounter = {
        "resourceType": "Encounter",
        "id": "encounter-1",
        "status": "in-progress",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "IMP",
            "display": "inpatient encounter"
        },
        "subject": {"reference": "Patient/123456789"},
        "participant": [{
            "individual": {
                "reference": "Practitioner/12345",
                "display": "Dr. Anna Smith"
            }
        }],
        "location": [{
            "location": {
                "display": "ICU Room 123 Bed B1"
            }
        }],
        "period": {
            "start": now_iso
        }
    }

    bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {"resource": patient, "request": {"method": "POST", "url": "Patient"}},
            {"resource": related_person, "request": {"method": "POST", "url": "RelatedPerson"}},
            {"resource": encounter, "request": {"method": "POST", "url": "Encounter"}},
        ]
    }

    return json.dumps(bundle, indent=2)


def send_fhir_message(fhir_server_url):
    headers = {"Content-Type": "application/fhir+json"}
    fhir_data = build_fhir_bundle()

    response = requests.post(fhir_server_url, data=fhir_data, headers=headers)
    if response.status_code in [200, 201]:
        print("FHIR message sent successfully")
        print("Response:\n", response.json())
    else:
        print(f"Error sending FHIR message: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    FHIR_SERVER = "http://192.168.1.98:5000/api/fhir" # CHANGE URL WITH YOUR FHIR SERVER
    send_fhir_message(FHIR_SERVER)