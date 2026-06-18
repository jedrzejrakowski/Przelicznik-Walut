"""Testy logiki wyboru daty kursu i przeliczenia (bez dostępu do sieci)."""

import datetime as dt

import nbp


def test_dzien_powszedni_bierze_dzien_poprzedni():
    # Środa 2024-06-12 -> kurs z wtorku 2024-06-11.
    assert nbp.select_rate_date(dt.date(2024, 6, 12)) == dt.date(2024, 6, 11)


def test_poniedzialek_cofa_do_piatku():
    # Poniedziałek 2024-06-10: poprzedni dzień to niedziela -> piątek 2024-06-07.
    assert nbp.select_rate_date(dt.date(2024, 6, 10)) == dt.date(2024, 6, 7)


def test_niedziela_cofa_do_piatku():
    # Niedziela 2024-06-09: poprzedni dzień to sobota -> piątek 2024-06-07.
    assert nbp.select_rate_date(dt.date(2024, 6, 9)) == dt.date(2024, 6, 7)


def test_sobota_bierze_piatek():
    # Sobota 2024-06-08: poprzedni dzień to piątek 2024-06-07 (dzień roboczy).
    assert nbp.select_rate_date(dt.date(2024, 6, 8)) == dt.date(2024, 6, 7)


def test_konwersja_zaokragla_do_dwoch_miejsc():
    assert nbp.convert_to_pln(100, 4.3215) == 432.15
    assert nbp.convert_to_pln(33.33, 4.5) == 149.99


if __name__ == "__main__":
    import sys

    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)
