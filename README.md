# Przelicznik walut na PLN (kurs NBP)

Aplikacja przeliczająca kwotę w walucie obcej na złotówki według **średniego
kursu NBP (tabela A)**. Obsługiwane waluty: **EUR, USD, GBP, CHF**.

Dostępna w dwóch wariantach:

- **`PrzelicznikWalut.html`** – wersja przeglądarkowa. Otwierasz dwuklikiem w
  Edge/Chrome. **Nie wymaga instalacji, Pythona ani uprawnień administratora**
  i nie jest blokowana przez antywirus (to nie jest plik `.exe`). Zalecana na
  komputerach firmowych z ograniczeniami.
- **`app.py`** – wersja desktopowa w PyQt6 (można skompilować do `.exe`).


Program pokazuje:
- przeliczoną kwotę w **PLN**,
- zastosowany **kurs** (PLN za 1 jednostkę waluty obcej),
- **datę kursu** oraz numer tabeli NBP.

## Reguła wyboru kursu

Do przeliczenia stosowany jest kurs z **dnia poprzedzającego zdarzenie
gospodarcze**. Jeżeli dzień poprzedzający wypada w **sobotę lub niedzielę**,
brany jest kurs z **ostatniego dnia roboczego poprzedniego tygodnia** (piątku).
Jeśli dla wyznaczonego dnia NBP nie opublikował tabeli (święto), program
automatycznie cofa się do wcześniejszego dnia roboczego.

Odpowiada to zasadzie z art. 30 ust. 2 ustawy o rachunkowości oraz przepisów
podatkowych (np. art. 11a ustawy o PIT).

## Uruchomienie ze źródeł

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Wymagany jest dostęp sieciowy do `https://api.nbp.pl` (publiczne API NBP).

## Kompilacja do pliku `.exe` (bez uprawnień administratora)

Na komputerze firmowym **nie potrzebujesz uprawnień administratora** —
wystarczy zainstalowany Python (instalacja „tylko dla mnie" / *Install for me
only* nie wymaga admina; pamiętaj o zaznaczeniu **Add Python to PATH**).

Następnie wystarczy uruchomić dołączony skrypt:

```bat
build_exe.bat
```

Skrypt sam, w lokalnym katalogu (bez zapisu do `C:\Program Files`):
1. tworzy wirtualne środowisko `.venv`,
2. instaluje PyQt6 i PyInstaller tylko dla bieżącego użytkownika,
3. buduje plik **`dist\PrzelicznikWalut.exe`**.

Gotowy `PrzelicznikWalut.exe` to pojedynczy plik — można go skopiować i
uruchamiać na innych komputerach z Windows (Python nie jest tam potrzebny).

> Gdyby `build_exe.bat` nie zadziałał, te same kroki ręcznie:
> ```bat
> python -m venv .venv
> .venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
> .venv\Scripts\pyinstaller.exe --onefile --windowed --name PrzelicznikWalut app.py
> ```

## Testy

Testy logiki (reguła daty + zaokrąglanie) nie wymagają sieci:

```bash
python test_nbp.py
```

## Pliki projektu

| Plik | Opis |
|------|------|
| `app.py` | Interfejs graficzny PyQt6 |
| `nbp.py` | Pobieranie kursów z NBP + reguła wyboru daty |
| `test_nbp.py` | Testy logiki |
| `build_exe.bat` | Budowanie `.exe` bez uprawnień administratora |
| `requirements.txt` | Zależności |
| `icon.ico` / `icon.png` | Ikona aplikacji (okno + plik `.exe`) |
| `make_icon.py` | Skrypt generujący ikonę (wymaga `pillow`) |
