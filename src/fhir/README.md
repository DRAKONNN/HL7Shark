HL7 FHIR
==============
**HL7 FHIR** (Fast Healthcare Interoperability Resources) is a standard for exchanging healthcare information electronically. It's developed by **HL7** (Health Level Seven International) and is designed to make it easier for healthcare systems to share data. HL7 FHIR Combines the best features of previous HL7 standards (like HL7 v2, v3, and CDA) with modern web technologies like RESTful APIs, JSON, and XML.

## 🏥Example use cases
- A mobile app retrieving a patient’s allergies via a FHIR API.
- A hospital system sending lab results to a specialist’s system.
- Public health organizations aggregating COVID-19 test data from multiple sources.

---

I have designed an **API** to handle the **JSON** messages that `client_fhir.py` would send, for example.
To start using it, run this command:
```
$ uvicorn api_fhir:app --host=0.0.0.0 --port=5000
```

## 🔥Fireshark
We could intercept the **FHIR** message between a `client_fhir.py` and `api_fhir.py` with the following command:
```
$ tshark -i lo -f "tcp port 5000" -Y 'http.request.method == POST && http.content_type contains "application/fhir+json"' -T fields -e frame.time -e ip.src -e ip.dst -e http.request.uri -e http.request.method -e http.file_data
```