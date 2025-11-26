# Remote Access mit Cloudflare Tunnel

Dieser Guide zeigt dir, wie du deinen Zettelkasten-MCP-Server über Cloudflare Tunnel remote verfügbar machst, sodass du ihn von überall (auch vom Handy) nutzen kannst.

## 🎯 Vorteile dieser Lösung

- ✅ **Kostenlos** - Cloudflare Tunnel ist gratis
- ✅ **Daten bleiben lokal** - Alle Notizen und die Datenbank bleiben auf deinem Rechner
- ✅ **Sicher** - Automatisches HTTPS, keine Ports öffnen nötig
- ✅ **Einfach** - Setup in 15-30 Minuten
- ✅ **Von überall erreichbar** - Web, Desktop, Mobile

## 📋 Voraussetzungen

- Ein Cloudflare-Account (kostenlos)
- Ein Domain-Name (optional, Cloudflare stellt auch eine kostenlose Subdomain bereit)
- Python 3.10 oder höher
- Dein Rechner muss laufen, wenn du remote zugreifen willst

## 🚀 Setup-Anleitung

### Schritt 1: Dependencies installieren

```bash
# Ins Projektverzeichnis wechseln
cd zettelkasten-mcp

# Virtual Environment aktivieren (falls noch nicht aktiv)
source .venv/bin/activate  # macOS/Linux
# oder
.venv\Scripts\activate  # Windows

# Neue Dependencies installieren
uv sync
```

### Schritt 2: .env-Datei erstellen

```bash
# Kopiere die Beispiel-Konfiguration
cp .env.example .env

# Optional: Passe die Konfiguration an
# Die Standardwerte funktionieren für lokalen Zugriff
```

### Schritt 3: HTTP-Server testen

```bash
# Starte den HTTP-Server
python -m zettelkasten_mcp.http_server

# Der Server läuft jetzt auf http://127.0.0.1:8080
```

Teste den Server in einem anderen Terminal:

```bash
# Health-Check
curl http://127.0.0.1:8080/health

# Server-Info
curl http://127.0.0.1:8080/

# MCP Initialize
curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "clientInfo": {"name": "test", "version": "1.0"}
    }
  }'
```

### Schritt 4: Cloudflare Tunnel installieren

#### macOS (mit Homebrew)
```bash
brew install cloudflare/cloudflare/cloudflared
```

#### Linux
```bash
# Debian/Ubuntu
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Oder direkt als Binary
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

#### Windows
```powershell
# Mit winget
winget install --id Cloudflare.cloudflared

# Oder manuell von
# https://github.com/cloudflare/cloudflared/releases
```

### Schritt 5: Cloudflare Tunnel einrichten

```bash
# 1. Bei Cloudflare anmelden (öffnet Browser)
cloudflared tunnel login

# 2. Tunnel erstellen
cloudflared tunnel create zettelkasten-mcp

# Dies erstellt:
# - Einen Tunnel mit einer UUID
# - Eine credentials-Datei in ~/.cloudflared/

# 3. Notiere die Tunnel-ID (wird ausgegeben)
# z.B.: Created tunnel zettelkasten-mcp with id 12345678-1234-1234-1234-123456789abc
```

### Schritt 6: Tunnel konfigurieren

Erstelle eine Konfigurationsdatei `~/.cloudflared/config.yml`:

```yaml
tunnel: DEINE-TUNNEL-ID
credentials-file: /home/DEIN-USERNAME/.cloudflared/DEINE-TUNNEL-ID.json

ingress:
  - hostname: zettelkasten.DEINE-DOMAIN.com
    service: http://127.0.0.1:8080
  - service: http_status:404
```

**Alternativ (ohne eigene Domain):**

Du kannst auch die kostenlose `trycloudflare.com` Subdomain nutzen:

```bash
# Schnellstart ohne Konfiguration (temporäre URL)
cloudflared tunnel --url http://127.0.0.1:8080
```

Dies gibt dir eine temporäre URL wie `https://random-words-1234.trycloudflare.com`

### Schritt 7: DNS konfigurieren (falls eigene Domain)

```bash
# Route erstellen (falls eigene Domain)
cloudflared tunnel route dns zettelkasten-mcp zettelkasten.DEINE-DOMAIN.com
```

### Schritt 8: Tunnel starten

```bash
# Option A: Mit Konfigurationsdatei (permanenter Tunnel)
cloudflared tunnel run zettelkasten-mcp

# Option B: Quick-Tunnel (temporäre URL, kein Login nötig)
cloudflared tunnel --url http://127.0.0.1:8080
```

### Schritt 9: Als Systemdienst einrichten (optional)

Damit der Tunnel automatisch bei Systemstart läuft:

#### Linux (systemd)
```bash
# Systemd-Service installieren
sudo cloudflared service install

# Service starten
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Status prüfen
sudo systemctl status cloudflared
```

#### macOS (launchd)
```bash
# Service installieren
sudo cloudflared service install

# Service starten
sudo launchctl load /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
```

#### Windows (Service)
```powershell
# Als Administrator ausführen
cloudflared service install
```

## 🔒 Sicherheit mit Cloudflare Access (empfohlen)

Um deinen Server mit OAuth zu schützen:

### 1. Cloudflare Zero Trust einrichten

1. Gehe zu https://one.dash.cloudflare.com/
2. Erstelle ein Zero Trust-Account (kostenlos bis 50 Nutzer)
3. Navigiere zu **Access** → **Applications**

### 2. Application erstellen

```yaml
Name: Zettelkasten MCP
Domain: zettelkasten.DEINE-DOMAIN.com
Type: Self-hosted

Policy:
  Name: Allow myself
  Action: Allow
  Include:
    - Emails: deine@email.com
```

### 3. Authentication Method wählen

- **One-time PIN** (einfachste Option)
- **Google/GitHub OAuth**
- **Microsoft Azure AD**
- Andere Identity Provider

Jetzt musst du dich erst authentifizieren, bevor du auf den Server zugreifen kannst!

## 📱 Claude Mobile einrichten

### 1. Remote MCP Server hinzufügen

1. Öffne Claude App auf dem Handy
2. Gehe zu **Settings** → **Custom Connectors**
3. Tippe auf **Add Remote MCP Server**
4. Gib deine Server-URL ein:
   ```
   https://zettelkasten.DEINE-DOMAIN.com/mcp
   ```

### 2. Authentication (falls Cloudflare Access aktiviert)

- Beim ersten Zugriff wirst du zur Cloudflare-Login-Seite weitergeleitet
- Nach erfolgreicher Authentifizierung wird ein Cookie gesetzt
- Claude kann jetzt auf deinen Zettelkasten zugreifen!

### 3. Tools testen

In Claude Mobile kannst du jetzt Befehle nutzen wie:

```
Erstelle eine neue Notiz mit dem Titel "Testnotiz" und dem Inhalt "Das ist ein Test"
```

Claude wird automatisch das `zk_create_note` Tool nutzen!

## 🛠️ Troubleshooting

### Server startet nicht

```bash
# Prüfe ob Port 8080 frei ist
lsof -i :8080

# Oder ändere den Port in .env
HTTP_PORT=8081
```

### Tunnel verbindet nicht

```bash
# Prüfe Tunnel-Status
cloudflared tunnel info zettelkasten-mcp

# Logs anschauen
cloudflared tunnel run zettelkasten-mcp --loglevel debug
```

### CORS-Fehler im Browser

Füge die Claude-Domains zu `ALLOWED_ORIGINS` in `.env` hinzu:

```bash
ALLOWED_ORIGINS=https://claude.ai,https://api.anthropic.com
```

### Datenbank-Fehler

```bash
# Stelle sicher dass das data-Verzeichnis existiert
mkdir -p data/notes data/db

# Index neu erstellen (in Claude)
Führe das Tool zk_rebuild_index aus
```

## 📊 Monitoring

### Server-Logs

```bash
# Mit erhöhtem Log-Level starten
python -m zettelkasten_mcp.http_server --log-level DEBUG
```

### Cloudflare Dashboard

- Besuche https://dash.cloudflare.com/
- Navigiere zu **Traffic** → **Analytics**
- Sieh Requests, Bandbreite und Fehler

## 🔄 Updates

```bash
# Code aktualisieren
git pull origin main

# Dependencies aktualisieren
uv sync

# Server neu starten
# (Systemd)
sudo systemctl restart cloudflared

# Oder manuell stoppen und neu starten
```

## 💡 Tipps

### Automatischer Start beim Systemstart

Erstelle ein Startup-Script `start_zettelkasten.sh`:

```bash
#!/bin/bash
cd /pfad/zu/zettelkasten-mcp
source .venv/bin/activate
python -m zettelkasten_mcp.http_server &
```

Füge es zu deinem Autostart hinzu (je nach OS unterschiedlich).

### Bessere Logs

Installiere ein Tool wie `pm2` (Node.js) oder `supervisor`:

```bash
# Mit PM2
npm install -g pm2
pm2 start "python -m zettelkasten_mcp.http_server" --name zettelkasten
pm2 startup
pm2 save
```

### Backups

Deine Daten sind lokal, also sichere regelmäßig:

```bash
# Einfaches Backup-Script
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Oder mit rsync
rsync -av data/ /pfad/zum/backup/
```

## 📚 Weitere Ressourcen

- [Cloudflare Tunnel Dokumentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Cloudflare Access Dokumentation](https://developers.cloudflare.com/cloudflare-one/policies/access/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)

## ❓ Häufige Fragen

**Q: Kostet das was?**
A: Nein! Cloudflare Tunnel und Zero Trust sind für bis zu 50 Nutzer kostenlos.

**Q: Kann ich mehrere Geräte verbinden?**
A: Ja! Du kannst Claude Desktop, Claude Mobile und Claude Web gleichzeitig nutzen.

**Q: Was passiert wenn mein Rechner aus ist?**
A: Der Server ist dann nicht erreichbar. Für 24/7 Verfügbarkeit brauchst du eine Cloud-Lösung.

**Q: Ist das sicher?**
A: Ja! Cloudflare Tunnel nutzt verschlüsselte Verbindungen und mit Cloudflare Access hast du zusätzlichen OAuth-Schutz.

**Q: Kann ich das mit anderen MCP-Servern nutzen?**
A: Ja! Diese Anleitung funktioniert für jeden HTTP-basierten MCP-Server.

## 🎉 Fertig!

Dein Zettelkasten ist jetzt von überall erreichbar! 🚀

Viel Spaß beim Notizen machen! 📝
