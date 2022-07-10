import configparser
import os
from datetime import datetime

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QMessageBox

from google_fit_api import google_fit_api


class weight_fat_input(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        if not os.path.exists('config.ini'):
            self.config = configparser.RawConfigParser()
            self.config.add_section('Weight')
            self.config.set('Weight', 'data_source_id', '')
            self.config.set('Weight', 'data_type', '')
            self.config.add_section('Fat')
            self.config.set('Fat', 'data_source_id', '')
            self.config.set('Fat', 'data_type', '')
            with open('config.ini', 'w') as file:
                self.config.write(file)
        else:
            self.config = configparser.ConfigParser()
            self.config.read('config.ini')

        self.weight = QLineEdit()
        self.weight.setValidator(QDoubleValidator(0.0, 100, 1, notation=QDoubleValidator.StandardNotation))

        self.fat = QLineEdit()
        self.fat.setValidator(QDoubleValidator(0.99, 99.99, 2))

        self.year = QLineEdit()
        self.month = QLineEdit()
        self.day = QLineEdit()
        self.hour = QLineEdit()
        self.minute = QLineEdit()
        self.second = QLineEdit()
        self.btnPress1 = QPushButton("Upload")

        self.year.setText(str(datetime.today().year))
        self.month.setText(str(datetime.today().month))
        self.day.setText(str(datetime.today().day))
        self.hour.setText(str(datetime.today().hour))
        self.minute.setText(str(datetime.today().minute))
        self.second.setText(str(0))

        flo = QFormLayout()
        flo.addRow("Weight [kg]", self.weight)
        flo.addRow("Fat percentage [%]", self.fat)
        flo.addRow("Year", self.year)
        flo.addRow("month", self.month)
        flo.addRow("day", self.day)
        flo.addRow("hour", self.hour)
        flo.addRow("minute", self.minute)
        flo.addRow("second", self.second)
        layout = QVBoxLayout()
        layout.addLayout(flo)
        layout.addWidget(self.btnPress1)

        self.setLayout(layout)
        self.setWindowTitle("Weight/Fat uploader")

        self.btnPress1.clicked.connect(self.btnSend_clicked)

    def btnSend_clicked(self):
        try:
            weight = float(self.weight.text())
            fat = float(self.fat.text())
            input_date = datetime(
                int(self.year.text()),
                int(self.month.text()),
                int(self.day.text()),
                int(self.hour.text()),
                int(self.minute.text()),
                int(self.second.text())
            )
            print(input_date)
        except ValueError:
            QMessageBox.critical(None, "Error", "It's not a value.")
        else:
            if fat < 0 or 100 < fat:
                QMessageBox.critical(None, "Range check", "Fat should be 0 <= Fat <= 100")
            elif weight < 0 or 1000 < weight:
                QMessageBox.critical(None, "Range check", "Weight should be 0 <= Weight <= 1000")
            else:
                result = QMessageBox.question(
                    None,
                    "Confirmation",
                    '{}\nWeight : {}[kg]\nFat : {}[%]\nAre you sure?'.format(input_date, weight, fat),
                    QMessageBox.Ok,
                    QMessageBox.Cancel
                )
                if result == QMessageBox.Ok:
                    self.input_daily_data(input_date, weight, fat)
                    QMessageBox.information(
                        None,
                        "Info",
                        'Done',
                        QMessageBox.Ok,
                    )

                else:
                    '''
                    Nothing to do
                    '''

    def input_daily_data(self, input_date, weight, fat):
        data_source_weight = self.config.get('Weight', 'data_source_id')
        data_type_weight = self.config.get('Weight', 'data_type')
        data_source_fat = self.config.get('Fat', 'data_source_id')
        data_type_fat = self.config.get('Fat', 'data_type')

        fit = google_fit_api()
        ret_weight = fit.insert_data_point(data_source_weight, data_type_weight, input_date, weight)
        ret_fat = fit.insert_data_point(data_source_fat, data_type_fat, input_date, fat)

        print(ret_weight)
        print(ret_fat)
