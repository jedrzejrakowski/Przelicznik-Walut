"""Przelicznik walut obcych na PLN – interfejs graficzny (PyQt6).

Aplikacja przelicza kwotę w walucie obcej (EUR, USD, GBP, CHF) na złotówki,
stosując średni kurs NBP z dnia poprzedzającego zdarzenie gospodarcze
(z uwzględnieniem weekendów i świąt – patrz moduł ``nbp``).

Uruchomienie:  python app.py
"""

from __future__ import annotations

import datetime as _dt
import os
import sys

from PyQt6.QtCore import QDate, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import nbp


def _resource_path(name: str) -> str:
    """Zwraca sciezke do zasobu – dziala tez po spakowaniu PyInstallerem."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


class RateWorker(QThread):
    """Wątek pobierający kurs z NBP, aby nie blokować interfejsu."""

    finished_ok = pyqtSignal(object)      # nbp.RateResult
    finished_err = pyqtSignal(str)

    def __init__(self, code: str, event_date: _dt.date) -> None:
        super().__init__()
        self._code = code
        self._event_date = event_date

    def run(self) -> None:  # noqa: D401 - metoda QThread
        try:
            result = nbp.fetch_rate(self._code, self._event_date)
            self.finished_ok.emit(result)
        except Exception as exc:  # noqa: BLE001 - przekazujemy komunikat do GUI
            self.finished_err.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Przelicznik walut na PLN – kurs NBP")
        icon_path = _resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setMinimumWidth(460)
        self._worker: RateWorker | None = None
        self._last_result: nbp.RateResult | None = None
        self._build_ui()

    # ------------------------------------------------------------------ UI --
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("Przeliczenie waluty obcej na PLN")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        root.addWidget(title)

        # --- Dane wejściowe ---
        form_box = QGroupBox("Dane do przeliczenia")
        form = QFormLayout(form_box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setDecimals(2)
        self.amount_input.setMaximum(1_000_000_000.0)
        self.amount_input.setGroupSeparatorShown(True)
        self.amount_input.setValue(100.0)
        form.addRow("Kwota w walucie obcej:", self.amount_input)

        self.currency_input = QComboBox()
        for code, name in nbp.SUPPORTED_CURRENCIES.items():
            self.currency_input.addItem(f"{code} – {name}", code)
        form.addRow("Waluta:", self.currency_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMaximumDate(QDate.currentDate())
        form.addRow("Data zdarzenia gospodarczego:", self.date_input)

        root.addWidget(form_box)

        # --- Przycisk ---
        self.convert_btn = QPushButton("Przelicz")
        self.convert_btn.setDefault(True)
        self.convert_btn.clicked.connect(self._on_convert)
        root.addWidget(self.convert_btn)

        # --- Wyniki ---
        self.result_box = QGroupBox("Wynik")
        result_layout = QVBoxLayout(self.result_box)

        self.pln_label = QLabel("—")
        self.pln_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a6e1a;")
        self.pln_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        result_layout.addWidget(self.pln_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        result_layout.addWidget(line)

        self.rate_label = QLabel("Kurs: —")
        self.rate_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        result_layout.addWidget(self.rate_label)

        self.date_label = QLabel("Data kursu: —")
        self.date_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        result_layout.addWidget(self.date_label)

        self.table_label = QLabel("Tabela NBP: —")
        self.table_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        result_layout.addWidget(self.table_label)

        root.addWidget(self.result_box)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666;")
        root.addWidget(self.status_label)

    # -------------------------------------------------------------- akcje --
    def _on_convert(self) -> None:
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "Uwaga", "Podaj kwotę większą od zera.")
            return

        code = self.currency_input.currentData()
        qdate = self.date_input.date()
        event_date = _dt.date(qdate.year(), qdate.month(), qdate.day())

        self.convert_btn.setEnabled(False)
        self.status_label.setText("Pobieranie kursu z NBP…")

        self._worker = RateWorker(code, event_date)
        self._worker.finished_ok.connect(lambda res: self._on_rate(res, amount))
        self._worker.finished_err.connect(self._on_error)
        self._worker.start()

    def _on_rate(self, result: nbp.RateResult, amount: float) -> None:
        self._last_result = result
        pln = nbp.convert_to_pln(amount, result.rate)

        self.pln_label.setText(
            f"{amount:,.2f} {result.code}  =  {pln:,.2f} PLN".replace(",", " ")
        )
        self.rate_label.setText(
            f"Kurs średni NBP: 1 {result.code} = {result.rate:.4f} PLN"
        )
        self.date_label.setText(
            f"Data kursu: {result.effective_date.isoformat()} "
            f"(wyznaczony dzień: {result.requested_date.isoformat()})"
        )
        self.table_label.setText(f"Tabela NBP: {result.table_no}")
        self.status_label.setText("Gotowe.")
        self.convert_btn.setEnabled(True)

    def _on_error(self, message: str) -> None:
        self.status_label.setText("")
        self.convert_btn.setEnabled(True)
        QMessageBox.critical(
            self,
            "Błąd pobierania kursu",
            "Nie udało się pobrać kursu z NBP.\n\n"
            f"Szczegóły: {message}\n\n"
            "Sprawdź połączenie z internetem (api.nbp.pl) lub wybierz inną datę.",
        )


def main() -> int:
    app = QApplication(sys.argv)
    icon_path = _resource_path("icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
