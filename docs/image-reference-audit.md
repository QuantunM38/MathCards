# MathCards: Prüfung vom 30. Oktober 2026

Ausgangscommit: `028dbb7eedf60bbc6b8faee98794cba9474ee775` (`main`).
Alle zehn JSON-Dateien wurden vollständig gelesen und erfolgreich geparst.
Alle image-URLs beginnen mit
`https://raw.githubusercontent.com/QuantunM38/MathCards/main/`.

| JSON | Referenz | Original | Vorher exakt | Mit Patch exakt |
|---|---|---|---|---|
| 0001.json | image/0001.png | image/0001.png | Ja | Ja |
| 0002.json | image/0002.png | image/0002.PNG | Nein | Ja |
| 0003.json | image/0003.png | image/0003.PNG | Nein | Ja |
| 0004.json | image/0004.png | image/0004.PNG | Nein | Ja |
| 0005.json | image/0005.png | image/0005.PNG | Nein | Ja |
| 0006.json | image/0006.png | image/0006.PNG | Nein | Ja |
| 0007.json | image/0007.png | image/0007.PNG | Nein | Ja |
| 0008.json | image/0008.png | image/0008.PNG | Nein | Ja |
| 0009.json | image/0009.png | image/0009.PNG | Nein | Ja |
| 0010.json | image/0010.png | image/0010.PNG | Nein | Ja |

## Vergleich und Entscheidung

| Lösung | Wirkung | Risiko bei vorhandenen Veröffentlichungen |
|---|---|---|
| Originale nach .png umbenennen | JSON-URLs funktionieren | Externe .PNG-Links entfallen |
| JSON-Referenzen nach .PNG ändern | Bestehende Bilder werden referenziert | Metadatenbytes ändern sich; unveränderliche oder gecachte JSON-Kopien bleiben falsch |
| Bytegleiche .png-Dateien ergänzen (gewählt) | Beide Schreibweisen verfügbar | Zusätzlicher Checkout-Speicher; Namenskollisionen auf Dateisystemen ohne Groß-/Kleinschreibung |

Neun normale Dateien werden hinzugefügt, keine Symlinks oder Redirects.
Git verwendet dieselben Bild-Blobs für beide Pfade. Alle Originalbilder,
Metadaten und das README bleiben bytegleich. `tests/original_sha256.json`
sichert die SHA-256-Werte aller 21 Originaldateien und den Ausgangscommit.
Diese Prüfsummen nicht automatisch neu erzeugen, um Änderungen durchzuwinken.

Checkout und Tests benötigen ein Dateisystem mit Groß-/Kleinschreibung:
Linux oder unter Windows das Linux-Dateisystem von WSL, nicht `/mnt/c`.
Windows-Standarddateisysteme können die Schreibweisen nicht zuverlässig
getrennt darstellen. Der Test prüft Git-Pfade und Verzeichniseinträge exakt.
Die CI verwendet Ubuntu.

## Tatsächlich ausgeführte Prüfungen

Umgebung: Linux, Python 3.12.14, keine zusätzlichen Python-Pakete.

1. `git ls-tree -r HEAD`, Lesen sämtlicher Metadaten und README sowie
   `git log -5 --oneline`: Ausgangsbestand nur README, zehn Bilder, zehn JSONs;
   keine Vertragsdateien oder Deploymentdaten. Keine AGENTS.md gefunden.
2. Vor den Bildkopien: `python -m unittest discover -s tests -v`:
   sechs Testmethoden, 18 fehlgeschlagene Untertests (neun Referenzen und neun
   fehlende Kopien). Originalintegrität und drei Validator-Tests bestanden.
3. Nach Ergänzung und `git add`: derselbe Befehl, **6 Tests bestanden**.
   Zehn Referenzen exakt vorhanden, neun Kopien bytegleich und alle 21
   Originaldateien SHA-256-identisch.
4. Regressionstests erkennen falsche Groß-/Kleinschreibung, nicht versionierte
   Dateien, falsche URL-Präfixe, Traversal, Query/Fragment und kodierte Pfade.
   Die bestehende URL wird korrekt zugeordnet.
5. `git diff --cached --check`: erfolgreich, keine Whitespace-Fehler.
6. HTTP-GET mittels Python urllib gegen den unveränderten main-Stand:
   `image/0002.png`: **404**; `image/0002.PNG`: **200**, **3.755.630 Bytes** gelesen.
   Dies ist eine aktuelle Stichprobe, kein HTTP-Test aller zehn Bilder.

GitHub Actions ist für Push und Pull Requests konfiguriert, mit ausschließlich
lesenden Repository-Rechten und denselben Offline-Tests. Lokale Testergebnisse
sind kein Nachweis eines abgeschlossenen GitHub-Actions-Laufs.

## Grenzen und Übernahme

Eine NFT-Veröffentlichung ist weiterhin ungeklärt. Der Repository-Bestand
enthält keine belegte Vertragsadresse oder Token-URI-Liste. Wallets, Verträge,
Token-URIs und Plattformdaten wurden nicht geändert; keine Blockchain-
Transaktionen, Metadaten-Neuveröffentlichung oder Plattform-Refresh ausgeführt.

Der Patch wird getrennt zur Prüfung bereitgestellt; main bleibt unverändert.
Erst eine spätere Übernahme nach main repariert die derzeitigen main-Bild-URLs.
Danach alle zehn Bild-URLs und die alten .PNG-URLs per HTTP prüfen und bei
bekannten Veröffentlichungen die tatsächlich verwendeten Token-URIs lesen.
Commit-gebundene URLs, unabhängige IPFS-Kopien und Plattform-Caches werden durch
zusätzliche Dateien auf main nicht automatisch repariert.
