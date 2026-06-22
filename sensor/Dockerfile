# Capteur de scan ARO — sniffer scapy (nécessite le réseau de l'hôte + NET_RAW)
FROM python:3.12-slim

# libpcap pour la capture de paquets via scapy
RUN apt-get update && apt-get install -y --no-install-recommends libpcap0.8 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY nmap_sensor.py simulate_scan.py ./

CMD ["python", "nmap_sensor.py"]
