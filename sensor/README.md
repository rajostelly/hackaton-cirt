# Capteur de scan nmap — ARO

Détecte en temps réel les balayages de ports (nmap) contre le serveur exposé par
`sfyrisec.duckdns.org` et envoie une alerte à l'API ARO, qui l'affiche
instantanément sur le dashboard via SSE.

## Comment ça marche

```
attaquant --nmap--> serveur (sfyrisec.duckdns.org)
                       │  (le capteur sniffe les SYN TCP entrants)
                       ▼
        nmap_sensor.py  --POST /detections/scan-->  ARO API
                                                       │ crée une alerte
                                                       │ + push SSE
                                                       ▼
                                                  Dashboard (temps réel)
```

Un scan est détecté quand une même IP source touche ≥ `SCAN_PORT_THRESHOLD`
ports distincts dans `SCAN_WINDOW_SECONDS`. La criticité dépend du nombre de
ports (voir `aro.domain.detection.services.classify_scan`).

## Lancer sur le serveur (détection réelle)

Le sniffing exige les privilèges réseau (root / `CAP_NET_RAW`) et le **réseau de
l'hôte** (pour voir le trafic réel arrivant sur la machine).

### En direct (Linux)
```bash
cd sensor
pip install -r requirements.txt
sudo ARO_API_URL=http://localhost:8000 python nmap_sensor.py
```

### Via Docker Compose
Depuis `ARO-Hackaton/` :
```bash
docker compose up --build sensor
```
Le service `sensor` utilise `network_mode: host` et `cap_add: NET_RAW` afin de
capturer le trafic réel de la machine.

## Démo sans root (simulateur)

Pour montrer le pipeline temps réel sans lancer un vrai nmap :
```bash
cd sensor
pip install requests
python simulate_scan.py                 # scan de ports aléatoire
python simulate_scan.py --type vuln_scan
python simulate_scan.py --ports 200 --source-ip 203.0.113.66
```

Ou directement en HTTP :
```bash
curl -X POST http://localhost:8000/detections/scan \
  -H 'Content-Type: application/json' \
  -d '{"source_ip":"203.0.113.66","scan_type":"port_scan","ports":[22,80,443,3306,8080,9200,5601,1514,55000,21,23,25],"target":"sfyrisec.duckdns.org"}'
```

## Tester avec un vrai nmap

Depuis une autre machine, contre le serveur :
```bash
nmap -p 1-1000 sfyrisec.duckdns.org      # scan de ports -> alerte HIGH/CRITICAL
```
> ⚠️ Ne scannez que des hôtes qui vous appartiennent ou pour lesquels vous avez
> une autorisation explicite.
