import sys
import mysql.connector
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from design import Ui_Chemical_Usage

class MainApp(QMainWindow, Ui_Chemical_Usage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.button_submit.clicked.connect(self.on_submit)
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='chemical_usage'
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def cari_pemakaian(self, ph, turbidity, flowrate, durasi):
        query = "SELECT * FROM baseline WHERE ph = %s AND turbidity = %s"
        self.cursor.execute(query, (ph, turbidity))
        result = self.cursor.fetchone()

        if result:
            # Convert DECIMAL to float for calculations
            tawas = float(result['tawas'])
            naoh = float(result['naoh'])
            polimer = float(result['polimer'])

            total_tawas = tawas * flowrate * durasi / 1000  # gram -> kilogram
            total_naoh = naoh * flowrate * durasi / 1000    # gram -> kilogram
            total_polimer = polimer * flowrate * durasi / 1000  # gram -> kilogram

            return total_tawas, total_naoh, total_polimer
        else:
            return None, None, None

    def on_submit(self):
        try:
            ph = float(self.entry_ph.text())
            turbidity = float(self.entry_turbidity.text())
            flowrate = float(self.entry_flowrate.text())
            durasi = float(self.entry_durasi.text())

            tanggal = self.combobox_tanggal.currentText()
            bulan = self.combobox_bulan.currentText()
            tahun = self.combobox_tahun.currentText()
            nama = self.combobox_nama.currentText()
            shift = self.combobox_shift.currentText()

            total_tawas, total_naoh, total_polimer = self.cari_pemakaian(ph, turbidity, flowrate, durasi)

            if total_tawas is not None and total_naoh is not None and total_polimer is not None:
                QMessageBox.information(self, "Hasil", f"Pemakaian Tawas: {total_tawas:.2f} kilogram\nPemakaian NaOH: {total_naoh:.2f} kilogram\nPemakaian Polimer: {total_polimer:.2f} kilogram")

                self.simpan_ke_db(ph, turbidity, flowrate, durasi, total_tawas, total_naoh, total_polimer, tanggal, bulan, tahun, nama, shift)

                self.entry_ph.clear()
                self.entry_turbidity.clear()
                self.entry_flowrate.clear()
                self.entry_durasi.clear()

                self.combobox_tanggal.setCurrentIndex(0)
                self.combobox_bulan.setCurrentIndex(0)
                self.combobox_tahun.setCurrentIndex(0)
                self.combobox_nama.setCurrentIndex(0)
                self.combobox_shift.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Peringatan", "Data tidak ditemukan untuk nilai pH dan Turbidity yang diberikan.")
        except ValueError:
            QMessageBox.critical(self, "Error", "Masukkan nilai numerik yang valid untuk semua input.")

    def simpan_ke_db(self, ph, turbidity, flowrate, durasi, total_tawas, total_naoh, total_polimer, tanggal, bulan, tahun, nama, shift):
        try:
            query = """
                INSERT INTO report (tahun, bulan, tanggal, nama, shift, ph, turbidity, flowrate, operasional, tawas, csoda, polimer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (tahun, bulan, tanggal, nama, shift, ph, turbidity, flowrate, durasi, total_tawas, total_naoh, total_polimer))
            self.conn.commit()
            QMessageBox.information(self, "Info", "Data berhasil disimpan ke database")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat menyimpan ke database: {str(err)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
