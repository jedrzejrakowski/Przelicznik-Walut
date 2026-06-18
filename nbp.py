"""Pobieranie kursów walut z NBP oraz logika wyboru właściwej daty kursu.

Reguła księgowa (art. 30 ust. 2 ustawy o rachunkowości / art. 11a ustawy PIT):
do przeliczenia stosuje się średni kurs NBP (tabela A) z ostatniego dnia
roboczego poprzedzającego dzień zdarzenia gospodarczego.

W praktyce oznacza to:
* bierzemy dzień poprzedzający zdarzenie,
* jeśli wypada on w sobotę lub niedzielę, cofamy się do ostatniego dnia
  roboczego (piątku) poprzedniego tygodnia,
* jeśli dla wyznaczonego dnia NBP nie opublikował tabeli (święto), cofamy się
  o kolejne dni robocze aż do znalezienia notowania.

Moduł nie zależy od PyQt – dzięki temu można go łatwo testować i ponownie
wykorzystać.
"""

from __future__ import annotations

import datetime as _dt
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# Obsługiwane waluty (kod ISO 4217 -> pełna nazwa do wyświetlenia).
SUPPORTED_CURRENCIES = {
    "EUR": "Euro",
    "USD": "Dolar amerykański",
    "GBP": "Funt brytyjski",
    "CHF": "Frank szwajcarski",
}

# Bazowy adres API NBP (tabela A – kursy średnie).
_NBP_API = "http://api.nbp.pl/api/exchangerates/rates/a"

# Maksymalna liczba dni, o jaką cofamy się szukając notowania (długie święta).
_MAX_LOOKBACK_DAYS = 10


@dataclass(frozen=True)
class RateResult:
    """Wynik pobrania kursu."""

    code: str            # kod waluty, np. "EUR"
    rate: float          # kurs średni NBP (PLN za 1 jednostkę waluty)
    effective_date: _dt.date  # data, z której pochodzi kurs
    table_no: str        # numer tabeli NBP, np. "118/A/NBP/2024"
    requested_date: _dt.date   # data wyznaczona przez regułę księgową


def select_rate_date(event_date: _dt.date) -> _dt.date:
    """Zwraca datę kursu zgodnie z regułą księgową.

    Bierzemy dzień poprzedzający zdarzenie; jeśli wypada on w sobotę lub
    niedzielę, cofamy się do najbliższego dnia roboczego (piątku).
    """
    candidate = event_date - _dt.timedelta(days=1)
    # weekday(): poniedziałek=0 ... sobota=5, niedziela=6
    while candidate.weekday() >= 5:
        candidate -= _dt.timedelta(days=1)
    return candidate


def _fetch_single(code: str, date: _dt.date, *, timeout: float = 10.0):
    """Pobiera kurs dla konkretnej daty. Zwraca dict z API lub None (404)."""
    url = f"{_NBP_API}/{code.lower()}/{date.isoformat()}/?format=json"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Przelicznik-Walut/1.0 (+https://api.nbp.pl)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            # Brak danych dla tego dnia (np. święto) – sygnalizujemy cofnięciem.
            return None
        raise


def fetch_rate(code: str, event_date: _dt.date, *, timeout: float = 10.0) -> RateResult:
    """Pobiera z NBP kurs właściwy dla danego zdarzenia gospodarczego.

    Najpierw wyznacza datę kursu regułą księgową, a następnie – gdy dla tej
    daty brak notowania (święto) – cofa się o kolejne dni robocze.
    """
    code = code.upper()
    if code not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Nieobsługiwana waluta: {code}")

    requested = select_rate_date(event_date)
    probe = requested
    for _ in range(_MAX_LOOKBACK_DAYS):
        data = _fetch_single(code, probe, timeout=timeout)
        if data is not None:
            rate_info = data["rates"][0]
            effective = _dt.date.fromisoformat(rate_info["effectiveDate"])
            return RateResult(
                code=code,
                rate=float(rate_info["mid"]),
                effective_date=effective,
                table_no=rate_info["no"],
                requested_date=requested,
            )
        # Cofamy się do poprzedniego dnia roboczego.
        probe -= _dt.timedelta(days=1)
        while probe.weekday() >= 5:
            probe -= _dt.timedelta(days=1)

    raise LookupError(
        f"Nie znaleziono kursu {code} w okolicach {requested.isoformat()} "
        f"(sprawdzono {_MAX_LOOKBACK_DAYS} dni wstecz)."
    )


def convert_to_pln(amount: float, rate: float) -> float:
    """Przelicza kwotę w walucie obcej na PLN.

    Używa ``Decimal`` z zaokrągleniem połówek w górę (ROUND_HALF_UP), tak jak
    przyjęto przy zaokrąglaniu kwot pieniężnych – dzięki temu np. 149,985 PLN
    daje 149,99 PLN, a nie 149,98 jak przy zaokrągleniu binarnym float.
    """
    value = Decimal(str(amount)) * Decimal(str(rate))
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
