@echo off
REM ============================================================================
REM  Budowanie pliku .exe przelicznika walut - BEZ uprawnien administratora.
REM
REM  Skrypt:
REM    1) tworzy lokalne srodowisko wirtualne (folder .venv w tym katalogu),
REM    2) instaluje PyQt6 oraz PyInstaller TYLKO dla biezacego uzytkownika,
REM    3) kompiluje aplikacje do pojedynczego pliku dist\PrzelicznikWalut.exe.
REM
REM  Wymagania: zainstalowany Python 3.10+ (zaznacz "Add Python to PATH"
REM  podczas instalacji - instalacja "tylko dla mnie" nie wymaga admina).
REM
REM  Uruchomienie: kliknij dwukrotnie ten plik lub wpisz w cmd:  build_exe.bat
REM ============================================================================

setlocal
cd /d "%~dp0"

echo.
echo [1/4] Tworzenie lokalnego srodowiska wirtualnego (.venv)...
python -m venv .venv
if errorlevel 1 (
    echo.
    echo BLAD: Nie udalo sie utworzyc srodowiska. Czy Python jest w PATH?
    echo Sprawdz komenda:  python --version
    pause
    exit /b 1
)

echo.
echo [2/4] Aktualizacja pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo.
echo [3/4] Instalacja zaleznosci (PyQt6 + PyInstaller)...
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo.
    echo BLAD: Instalacja zaleznosci nie powiodla sie.
    pause
    exit /b 1
)

echo.
echo [4/4] Kompilacja do pliku .exe...
".venv\Scripts\pyinstaller.exe" --noconfirm --onefile --windowed --name PrzelicznikWalut app.py
if errorlevel 1 (
    echo.
    echo BLAD: Kompilacja nie powiodla sie.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo  GOTOWE! Plik wykonywalny znajdziesz w:  dist\PrzelicznikWalut.exe
echo  Mozna go skopiowac i uruchamiac na komputerze bez Pythona.
echo ============================================================================
pause
endlocal
