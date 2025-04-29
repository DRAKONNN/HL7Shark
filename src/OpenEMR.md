HL7
==============
**HL7** is a set of international standards created to facilitate the electronic exchange of clinical information between healthcare information systems. It is based on plain text divided into segments containing patient data.
Many systems send it via **MLLP**, so traffic can be spied on with analyzers like **Wireshark**.

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

---
*Creado y documentado por [DRAKONNN](https://github.com/DRAKONNN)*
