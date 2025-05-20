HL7
==============
**HL7** is a set of international standards created to facilitate the electronic exchange of clinical information between healthcare information systems. It is based on plain text divided into segments containing patient data.
Many systems send it via **MLLP**, so traffic can be spied on with analyzers like **Wireshark**.

The message is encoded and divided into ***segments*** (`MSH`, `EVN`, `PID`, `NK1`...) that indicate the type of data that follows. Each ***segment*** has several ***pipes*** (`|`) that serve as separators between data and `^` to separate words.

This is an example of a complete HL7 message:
> 
    "MSH|^~\&|NYC_Health_ADT||||20080115153000||ADT^A01^ADT_A01|0123456789|P|2.5||||AL"
    "EVN||20080115153000||AAA|AAA|20080114003000"
    "PID|1|123456789^^^HOSP^MR|||RICHARDS^REED^NATHANIEL||19800101|M|||2222 HOME STREET^^ANN ARBOR^MI^12345^USA||555-555-2004\R\444-333-222|||M"
    "NK1|1|RICHARDS^SUE^STORM|SPO|2222 HOME STREET^^ANN ARBOR^MI^^USA"
    "PV1|1|I|ICU^123^B^1||||12345^Smith^Anna^MD"
>


## 🦈Wireshark
We can intercept the HL7 message between a `client.py` and `server.py` with the following commands.
First of all, we have to install wireshark in our Linux terminal:
```
$ sudo apt update && sudo apt install -y tshark
$ sudo usermod -aG wireshark $USER
$ newgrp wireshark
$ tshark --version
```
After installing it correctly, we need to know which **interface** we can use as `eth0` or `ens18`:
```
$ ip -br a
```
Then, we use the wireshark command with the available **interface**:
```
$ tshark -i <interface> -d tcp.port==5000,hl7 -f "tcp port 5000" -Y 'hl7 contains "ADT^A01^ADT_A01" && hl7 contains "PID" &&
 hl7 contains "NK1"' -O hl7 -V
```
---
If the client and server are running on the same local machine, the command is as follows:
```
$ tshark -i lo -d tcp.port==5000,hl7 -f "tcp port 5000" -Y 'hl7 contains "ADT^A01^ADT_A01" && hl7
 contains "PID" && hl7 contains "NK1"' -O hl7 -V
```

## 📦Docker compose
To run the `docker-compose.yml` and use **OpenEMR** and **MySQL** database, you have to install the docker images first:
```
$ docker --version
$ docker pull openemr/openemr:latest
$ docker pull mariadb:10.4
$ docker pull phpmyadmin/phpMyAdmin
```
Once we have the images, we can raise the containers:
```
$ docker images
$ docker compose -f docker-compose.yml up -d
```

Wait **5 minutes** for it to load and ensure that **OpenEMR** has loaded correctly:
```
$ docker ps
$ docker logs <id-openemr> -f
```

> Generating a RSA private key  
> .................................................++++  
> ......................................................................................................++++  
> writing new private key to '/etc/ssl/private/selfsigned.key.pem'  
> ...  
> Setting user 'www' as owner of openemr/ and setting file/dir permissions to 400/500  
> Default file permissions and ownership set, allowing writing to specific directories  
> Removing remaining setup scripts  
> Setup scripts removed, we should be ready to go now!  
>  
> Love OpenEMR? You can now support the project via the open collective:  
> ...
>  
> Starting cron daemon!  
> Starting apache!

---
These are the links and credentials for the services:

| Service    | Links                | Credentials     |
|------------|----------------------|-----------------|
| OpenEMR    | http://HOST-IP:80/   | admin:pass      |
| phpMyAdmin | http://HOST-IP:8083/ | openemr:openemr |

> ⚠️Note: Ports may vary depending on what is set in `docker-compose.yml`.

---
*Created and documented by [DRAKONNN](https://github.com/DRAKONNN)*
