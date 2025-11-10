# 🚀 Gyors Flask Indítás - Problémamegoldás

## ❌ Probléma: "Flask szerver nem fut az 5001-es porton"

Ez általában azt jelenti, hogy:
- Az 5001-es port **foglalt** egy régi/korrupt folyamat által
- Vagy a Flask szerver **nem tudott elindulni** (import hiba, stb.)

---

## ✅ Gyors Megoldás (3 lépés)

### **1. Port felszabadítása**

Futtasd ezt a PowerShell-ben:
```powershell
.\kill_port_5001.ps1
```

**Vagy manuálisan:**
```powershell
# Az 5001-es portot foglaló folyamatok leállítása
Get-NetTCPConnection -LocalPort 5001 | 
    Select-Object -ExpandProperty OwningProcess -Unique | 
    ForEach-Object { Stop-Process -Id $_ -Force }
```

### **2. Flask szerver indítása**

**Automatikus (ajánlott):**
```powershell
.\start_flask_safe.ps1
```

**Vagy manuálisan:**
```powershell
python app.py
```

### **3. Ellenőrzés**

Nyisd meg a böngészőben:
```
http://127.0.0.1:5001
```

Vagy PowerShell-ben:
```powershell
Invoke-WebRequest http://127.0.0.1:5001/api/status
```

---

## 🔧 Alternatív Megoldás: Másik Port Használata

Ha az 5001-es port folyamatosan problémás, a Flask **automatikusan talál szabad portot** (5001, 5002, 5003...).

A konzolon látod:
```
[INFO] Flask szerver indítása porton: 5002
```

Ekkor használd a **5002-es** portot a böngészőben!

---

## 🛠️ Részletes Diagnosztika

Ha még mindig nem működik:

### **1. Ellenőrizd hogy fut-e valami a porton:**
```powershell
netstat -ano | findstr :5001
```

### **2. Nézd meg mi az a folyamat:**
```powershell
Get-NetTCPConnection -LocalPort 5001 | 
    Select-Object OwningProcess | 
    ForEach-Object { Get-Process -Id $_.OwningProcess }
```

### **3. Flask import ellenőrzés:**
```powershell
python -c "from flask import Flask; print('Flask OK')"
```

### **4. App.py szintaxis ellenőrzés:**
```powershell
python -m py_compile app.py
```

---

## 💡 Prevenció (Hogy ne legyen újra)

A probléma oka: **zombie folyamatok** maradnak, amikor:
- Ctrl+C-vel állítod le a Flask szervert (rossz módszer)
- A terminál bezáródik futó Flask-nel
- Python exception miatt nem záródik le rendesen

**Jó gyakorlat:**
1. ✅ Mindig használd a `kill_port_5001.ps1` scriptet indítás előtt
2. ✅ Vagy az `start_flask_safe.ps1` scriptet (automatikusan felszabadítja)
3. ✅ Flask leállításhoz: Ctrl+C a terminálban ahol fut

---

## 📋 Gyors Parancsok Összefoglalása

```powershell
# 1. Port felszabadítása
.\kill_port_5001.ps1

# 2. Flask indítása
.\start_flask_safe.ps1

# 3. Ellenőrzés
Invoke-WebRequest http://127.0.0.1:5001/api/status
```

**Vagy egy sorban:**
```powershell
.\kill_port_5001.ps1; Start-Sleep -Seconds 2; Start-Process python -ArgumentList "app.py"
```

---

## ⚠️ Ha Semmi Nem Működik

1. **Restart a géped** - ez felszabadítja az összes foglalt portot
2. **Vagy használj másik portot** - változtasd meg az `app.py`-ban:
   ```python
   port = int(os.environ.get('PORT', 8080))  # 8080-es port
   ```
3. **Telepítsd újra a Flask-et:**
   ```powershell
   pip uninstall flask
   pip install flask
   ```

---

## ✅ Sikeres Indítás Jelzése

A Flask szerver sikeresen fut, ha:
- ✅ Konzolon látod: `Running on http://127.0.0.1:5001`
- ✅ Böngészőben: `http://127.0.0.1:5001` betöltődik
- ✅ API válaszol: `http://127.0.0.1:5001/api/status` JSON-t ad vissza

