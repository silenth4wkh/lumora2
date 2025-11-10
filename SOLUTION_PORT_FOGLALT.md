# 🔧 MEGOLDÁS: Port Foglalt Probléma

## ⚠️ A Probléma

Az 5001-es portot egy **"zombie" kapcsolat** foglalja (PID 2916, CloseWait állapot).
Ez általában akkor történik, amikor egy folyamat nem záródik le rendesen.

---

## ✅ **LEGEGYSZERŰBB MEGOLDÁS** (Ajánlott!)

### **Használd az automatikus port keresést!**

A Flask szerver **AUTOMATIKUSAN** talál szabad portot. Csak indítsd el:

```powershell
python app.py
```

A konzolon látod:
```
[INFO] Flask szerver indítása porton: 5002
```

Akkor használd a **5002-es portot**:
```
http://127.0.0.1:5002
```

**Ez MINDIG működik!** ✅

---

## 🔨 Alternatív Megoldások

### **1. Port automatikus ellenőrzés script**

Futtasd:
```powershell
.\check_flask_port.ps1
```

Ez automatikusan megkeresi, hogy melyik porton fut a Flask, és megnyitja a böngészőben.

---

### **2. Teljes restart (100% működik)**

**Windows restart:**
- Ez felszabadítja az összes foglalt portot
- Leghatékonyabb megoldás

---

### **3. Task Manager-rel manuális leállítás**

1. Nyomj **Ctrl+Shift+Esc** (Task Manager)
2. Menj a **"Details"** fülre
3. Keresd meg a **PID 2916**-ot (vagy bármely Python folyamatot)
4. Jobb klikk → **End Task**

---

### **4. PowerShell-lel erős leállítás**

```powershell
# Próbáld meg leállítani
Stop-Process -Id 2916 -Force

# Ha nem működik, próbáld meg a szülő folyamatot
$proc = Get-Process -Id 2916 -ErrorAction SilentlyContinue
if ($proc) {
    Get-Process -Id $proc.Id | Stop-Process -Force
}
```

---

## 🎯 **AJÁNLÁS: Ne foglalkozz a porttal!**

**Használd ezt a scriptet:**

```powershell
.\start_flask_anyway.ps1
```

Ez:
1. ✅ Elindítja a Flask szervert
2. ✅ Automatikusan talál szabad portot
3. ✅ Mutatja, hogy melyik porton fut

**Vagy egyszerűen:**

```powershell
python app.py
```

És nézd meg a konzol kimenetét - ott látod melyik porton fut!

---

## 📋 Port Ellenőrzés

Ha nem tudod, melyik porton fut:

```powershell
# 5001-től 5010-ig ellenőrzi
.\check_flask_port.ps1
```

Vagy manuálisan:
```powershell
# Próbáld meg sorban
Invoke-WebRequest http://127.0.0.1:5001/api/status
Invoke-WebRequest http://127.0.0.1:5002/api/status
Invoke-WebRequest http://127.0.0.1:5003/api/status
```

---

## ⚡ Gyors Checklist

- [ ] **Próbáltad az automatikus port keresést?** (`python app.py`)
- [ ] **Nézted meg a konzol kimenetét?** (ott látod melyik port)
- [ ] **Próbáltad a `check_flask_port.ps1` scriptet?**
- [ ] **Próbáltad másik portot?** (5002, 5003, stb.)

Ha mindegyik működik, akkor **nincs probléma!** A Flask automatikusan talál szabad portot.

---

## 💡 Prevenció

Hogy ne legyen újra:

1. ✅ **Mindig Ctrl+C-vel** állítsd le a Flask szervert (NE zárd be a terminált)
2. ✅ **Használd az automatikus port keresést** - ne erőltesd az 5001-et
3. ✅ **Ha beragad**, egyszerűen **restart a gépet**

---

## 🎉 Összefoglalás

**NE IDEJESÍTSD a port felszabadításával!**

Egyszerűen:
```powershell
python app.py
```

És használd azt a portot, amit a konzol mutat! 🚀

