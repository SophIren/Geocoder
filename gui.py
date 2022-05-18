import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
import DB
import settings
from request_parsing import GeoParser
from param_name_list import GeoParamNameList
from PyQt5 import QtCore


def show_message_box(title, description, error_type):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(description)
    msg.setIcon(error_type)

    msg.exec_()


class GeocoderView(QMainWindow):
    def __init__(self):
        super(GeocoderView, self).__init__()
        uic.loadUi("geocoder.ui", self)
        self.a = 0
        self.find_button.clicked.connect(self.find)
        self.choose_button.clicked.connect(self.choose_address)
        self.selected_item_index = None
        self.listWidget.itemSelectionChanged.connect(self.selection_changed)
        self.listWidget.itemDoubleClicked.connect(self.choose_address)
        self.addresses = []

    def keyPressEvent(self, e):
        if e.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.find()

    def find(self):
        address = self.address_entry.text()
        if address == "":
            return
        try:
            addresses = parser.parse(address)
            if len(addresses) == 0:
                show_message_box("Error", "Nothing found", QMessageBox.Warning)
        except IndexError:
            show_message_box("Error", "Invalid request", QMessageBox.Critical)
            return

        titles = []
        self.addresses = []
        for elem in addresses:
            self.addresses.append(
                GeoParamNameList(lat=elem[1], lon=elem[2], city=elem[3], street=elem[4], house=elem[5],
                                 postcode=elem[6]))
            titles.append(f"{elem[3]}, {elem[4]} {elem[5]}")
        self.listWidget.clear()
        self.listWidget.addItems(titles)

    def choose_address(self):
        if self.selected_item_index is None:
            return
        address_info = self.addresses[self.selected_item_index]
        self.fill_outputs(address_info.lat, address_info.lon, address_info.city, address_info.street,
                          address_info.house, address_info.postcode)

    def fill_outputs(self, latitude, longitude, city, street, building, index):
        self.latitude_output.setText(str(latitude))
        self.longitude_output.setText(str(longitude))
        self.city_output.setText(city)
        self.street_output.setText(street)
        self.building_output.setText(building)
        self.index_output.setText(str(index))

    def selection_changed(self):
        self.selected_item_index = self.listWidget.currentRow()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    geocoder = GeocoderView()
    db = DB.DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
                      settings.STREET_TABLE])
    parser = GeoParser(db)
    geocoder.show()
    sys.exit(app.exec())
