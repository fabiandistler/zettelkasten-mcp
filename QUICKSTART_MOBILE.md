# 📱 Quick Start: Zettelkasten auf dem Handy nutzen

Diese Anleitung zeigt dir den **schnellsten Weg**, um deinen Zettelkasten vom Handy aus zu nutzen.

⏱️ **Zeit:** 15-20 Minuten

## 🎯 Was du brauchst

- [ ] Python 3.10+ auf deinem Computer installiert
- [ ] Ein Cloudflare-Account (kostenlos registrieren auf [dash.cloudflare.com](https://dash.cloudflare.com))
- [ ] Claude App auf deinem Handy (iOS oder Android)

## 🚀 Los geht's!

### 1️⃣ Projekt vorbereiten (5 Minuten)

```bash
# Repository klonen (falls noch nicht geschehen)
git clone https://github.com/entanglr/zettelkasten-mcp.git
cd zettelkasten-mcp

# Dependencies installieren
uv venv
source .venv/bin/activate  # macOS/Linux
# ODER: .venv\Scripts\activate  # Windows

uv sync

# Konfiguration erstellen
cp .env.example .env
```

### 2️⃣ HTTP-Server starten (1 Minute)

```bash
# Einfach das Start-Script ausführen
./start_http_server.sh  # macOS/Linux
# ODER: start_http_server.bat  # Windows
```

✅ Server läuft jetzt auf `http://127.0.0.1:8080`

### 3️⃣ Cloudflare Tunnel installieren (3 Minuten)

#### macOS
```bash
brew install cloudflare/cloudflare/cloudflared
```

#### Linux
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

#### Windows
```powershell
winget install Cloudflare.cloudflared
```

### 4️⃣ Tunnel starten (1 Minute)

In einem **neuen Terminal** (der HTTP-Server läuft weiter im ersten Terminal):

```bash
cloudflared tunnel --url http://127.0.0.1:8080
```

Du bekommst eine URL wie:
```
https://random-words-1234.trycloudflare.com
```

🎉 **Diese URL ist dein Server-Link!** Notiere sie dir.

### 5️⃣ In Claude Mobile einrichten (2 Minuten)

1. **Claude App öffnen**
2. **Settings** → **Custom Connectors** (oder **Features**)
3. **Add Remote MCP Server**
4. **URL eingeben:**
   ```
   https://random-words-1234.trycloudflare.com/mcp
   ```
   ⚠️ Wichtig: `/mcp` am Ende nicht vergessen!
5. **Save**

### 6️⃣ Testen! 🎉

Sag in Claude:

```
Erstelle eine Notiz mit dem Titel "Meine erste mobile Notiz"
und dem Inhalt "Das funktioniert!"
```

Claude sollte antworten:
```
Note created successfully with ID: 20250126T123456
```

**✅ Geschafft!** Dein Zettelkasten läuft jetzt mobil! 🎊

## 🔄 Nächstes Mal nutzen

Wenn du deinen Zettelkasten das nächste Mal nutzen willst:

```bash
# Terminal 1: HTTP-Server starten
cd zettelkasten-mcp
./start_http_server.sh

# Terminal 2: Tunnel starten
cloudflared tunnel --url http://127.0.0.1:8080
```

Die URL ändert sich jedes Mal! Du musst sie in Claude Mobile aktualisieren.

## 💡 Permanente URL? (Optional)

Willst du eine **feste URL**, die sich nicht ändert?

👉 Siehe [REMOTE_ACCESS.md](REMOTE_ACCESS.md) für die Einrichtung eines permanenten Tunnels.

Das dauert 10 Minuten mehr, aber dann hast du:
- ✅ Feste URL (z.B. `zettelkasten.deine-domain.com`)
- ✅ Automatischer Start beim Systemstart
- ✅ Optional: OAuth-Authentifizierung

## 🛑 Server stoppen

```bash
# HTTP-Server stoppen
Ctrl + C (im ersten Terminal)

# Tunnel stoppen
Ctrl + C (im zweiten Terminal)
```

## ❓ Probleme?

### "Connection refused"
- ✅ Prüfe ob HTTP-Server läuft: `curl http://127.0.0.1:8080/health`
- ✅ Port 8080 frei? Ändere in `.env`: `HTTP_PORT=8081`

### "Tunnel not found"
- ✅ Cloudflared neu starten
- ✅ Neue URL in Claude Mobile eintragen

### "Tool not found" in Claude
- ✅ URL endet mit `/mcp`?
- ✅ Server-Logs prüfen im Terminal

### "CORS error"
- ✅ In `.env`: `ALLOWED_ORIGINS=*` (nur für Tests!)

## 📚 Nächste Schritte

Jetzt wo es funktioniert:

1. **Notizen erstellen** - `Erstelle eine Notiz...`
2. **Notizen verlinken** - `Verlinke Notiz A mit Notiz B`
3. **Suchen** - `Suche nach Notizen mit Tag "ideen"`
4. **Erkunden** - `Zeige mir verwaiste Notizen`

Alle verfügbaren Tools: [README.md#available-mcp-tools](README.md#available-mcp-tools)

## 🔐 Sicherheit

⚠️ **Wichtig:** Die temporäre URL ist öffentlich! Jeder der die URL kennt, kann auf deinen Zettelkasten zugreifen.

Für Produktiv-Nutzung:
- Richte [Cloudflare Access](REMOTE_ACCESS.md#-sicherheit-mit-cloudflare-access-empfohlen) ein (OAuth-Schutz)
- Oder: Nutze nur im privaten WLAN
- Backups erstellen: `tar -czf backup.tar.gz data/`

## 💬 Feedback?

Funktioniert es? Probleme? Ideen?

👉 [GitHub Issues](https://github.com/entanglr/zettelkasten-mcp/issues)

---

**Viel Spaß mit deinem mobilen Zettelkasten! 🎉**
