import sys
import folium
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap

map = folium.Map(location=[16.9083, 122.3941], zoom_start=8,control_scale=False, scrollWheelZoom=False, zoomControl=False, doubleClickZoom=False)
# folium.Marker([45.5236, -122.6750], popup="Click me!").add_to(m)
map.options['attributionControl'] = False
map.save("map.html")

class CordiMap(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('CordiMap')
        self.setGeometry(0, 0, 1500, 800)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile("D:/langmap/map.html"))
        self.setCentralWidget(self.browser)

        self.logo = QLabel(self)
        self.logo.setGeometry(50, 30, 200, 80) 
        logo = QPixmap("D:/langmap/cordilogo.png") 
        self.logo.setPixmap(logo.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setStyleSheet("background-color: transparent;")

    #     self.search_bar = QLineEdit(self)
    #     self.search_bar.setPlaceholderText("Enter location and click Search")
    #     self.search_bar.setGeometry(950, 50, 400, 40)
    #     self.search_bar.setStyleSheet("padding: 10px; font-family: Arial; font-size: 12px; border: none; border-radius: 15px;")
        
    #     self.search_btn = QPushButton("SEARCH", self)
    #     self.search_btn.setGeometry(1355, 50, 80, 40)
    #     self.search_btn.clicked.connect(self.search_loc)
    #     self.search_btn.setStyleSheet("padding: 5px; font-family: Arial; font-size: 12px;")

    # def search_loc(self):
    #     search_query = self.search_bar.text()
    #     if search_query:
    #         print(f"Searching for: {search_query}")
    #         folium.Marker([45.5236, -122.6750], popup=f"Search: {search_query}").add_to(map)
    #         map.save("map.html")
            
    #         self.browser.setUrl(QUrl.fromLocalFile("D:/langmap/map.html"))

cordimap = QApplication(sys.argv)
window = CordiMap()
window.show()

sys.exit(cordimap.exec_())
