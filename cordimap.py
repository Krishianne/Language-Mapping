import sys
import os 
import folium
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap

from folium import MacroElement
from jinja2 import Template


map = folium.Map(location=[16.9083, 122.3941], zoom_start=8,control_scale=False, scrollWheelZoom=False, zoomControl=False, doubleClickZoom=False)
# folium.Marker([45.5236, -122.6750], popup="Click me!").add_to(m)
map.options['attributionControl'] = False
map.save("map.html")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(BASE_DIR, "map.html")
LOGO_PATH = os.path.join(BASE_DIR, "cordilogo.png")

class CordiMap(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('CordiMap')
        self.setGeometry(0, 0, 1500, 800)
        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))
        self.setCentralWidget(self.browser)

        self.logo = QLabel(self)
        self.logo.setGeometry(50, 30, 200, 80) 
        logo = QPixmap(LOGO_PATH) 
        self.logo.setPixmap(logo.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setStyleSheet("background-color: transparent;")
        
        self.show_information_panel()
        self.header_panel()
    

    def header_panel(self):
    # --- Province Panel ---
        self.province_panel = QWidget(self)
        self.province_panel.setGeometry(950, 50, 240, 40)
        self.province_panel.setStyleSheet("background-color: #f2efe9; border-radius: 8px;")

        province_layout = QHBoxLayout()
        province_layout.setContentsMargins(10, 5, 10, 5)

        self.provinces = QComboBox()
        self.provinces.setFixedHeight(30)
        self.provinces.addItems(["Select Province", "Abra", "Apayao", "Benguet", "Ifugao", "Kalinga", "Mountain Province"])
        self.provinces.setStyleSheet("ComboBox { padding: 5px; font-family: Arial; font-size: 12px; background-color: f2efe9; }")
        self.provinces.currentIndexChanged.connect(self.on_province_selected)

        province_layout.addWidget(self.provinces)
        self.province_panel.setLayout(province_layout)

        # --- Municipality Panel ---
        self.municipality_panel = QWidget(self)
        self.municipality_panel.setGeometry(1200, 50, 240, 40)
        self.municipality_panel.setStyleSheet("background-color: #f2efe9; border-radius: 8px;")

        municipality_layout = QHBoxLayout()
        municipality_layout.setContentsMargins(10, 5, 10, 5)

        self.municipalities = QComboBox()
        self.municipalities.setFixedHeight(30)
        self.municipalities.addItems(["Select Municipality", "Bangued", "Calanasan", "La Trinidad", "Lagawe", "Tabuk", "Bontoc"])
        self.municipalities.setStyleSheet("ComboBox { padding: 5px; font-family: Arial; font-size: 12px; }")
        self.municipalities.setEnabled(False) 

        municipality_layout.addWidget(self.municipalities)
        self.municipality_panel.setLayout(municipality_layout)

        # --- Search Panel ---
        self.search_panel = QWidget(self)
        self.search_panel.setGeometry(950, 100, 490, 40)
        self.search_panel.setStyleSheet("background-color: #f2efe9; border-radius: 8px; ")

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(5)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter A Word")
        self.search_bar.setFixedHeight(30)
        self.search_bar.setStyleSheet("padding: 5px; font-family: Arial; font-size: 12px;")

        self.search_btn = QPushButton("SEARCH")
        self.search_btn.setFixedSize(80, 30)
        self.search_btn.setStyleSheet("font-family: Arial; font-size: 12px;")

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_btn)

        self.municipalities.currentIndexChanged.connect(self.selected_province_municipality)
        self.search_btn.clicked.connect(self.search_loc)

        self.search_panel.setLayout(search_layout)

    # Municipality disable/enable
    def on_province_selected(self, index):
        if index == 0:
            self.municipalities.setEnabled(False)
        else:
            self.municipalities.setEnabled(True)

    # Display selected province
    def selected_province_municipality(self, index):
        if self.provinces.currentIndex() != 0 and index != 0:
            province = self.provinces.currentText()
            municipality = self.municipalities.currentText()
            print(f"Province: {province}, Municipality: {municipality}")
            self.scroll_container.hide()

            self.create_dynamic_info_panel(province, municipality)

    def create_dynamic_info_panel(self, province, municipality):
        self.dynamic_scroll_container = QScrollArea(self)
        self.dynamic_scroll_container.setGeometry(950, 150, 490, 600)
        self.dynamic_scroll_container.setWidgetResizable(True)
        self.dynamic_scroll_container.setStyleSheet("""
            border: none;
            border-radius: 8px;
            background-color: #f2efe9;
        """)

        self.dynamic_info_panel = QWidget()
        self.dynamic_info_panel.setStyleSheet("background-color: #f2efe9; border-radius: 8px;")
        self.dynamic_scroll_container.setWidget(self.dynamic_info_panel)

        dynamic_info_layout = QVBoxLayout(self.dynamic_info_panel)
        dynamic_info_layout.setContentsMargins(20, 20, 20, 20)
        dynamic_info_layout.setSpacing(10)

        self.dynamic_title_label = QLabel(f"Information for {municipality}, {province}", self.dynamic_info_panel)
        self.dynamic_title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #34495e;")
        dynamic_info_layout.addWidget(self.dynamic_title_label)

        separator_line = QFrame(self.dynamic_info_panel)
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setStyleSheet("background-color: #000; margin-top: 2px; margin-bottom: 2px;")
        separator_line.setFixedHeight(1)
        dynamic_info_layout.addWidget(separator_line)

        self.dynamic_description_label = QLabel(self.get_dynamic_description(province, municipality), self.dynamic_info_panel)
        self.dynamic_description_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        self.dynamic_description_label.setWordWrap(True)
        dynamic_info_layout.addWidget(self.dynamic_description_label)


        self.dynamic_info_panel.setLayout(dynamic_info_layout)
        self.dynamic_scroll_container.show()

    def get_dynamic_description(self, province, municipality):
        descriptions = {
            "Abra": {
                "Bangued": "Bangued is the capital municipality of Abra, known for its rich cultural heritage.",
                "Calanasan": "Calanasan is a municipality in Abra, characterized by its mountain landscapes.",
            },
            "Apayao": {
                "Conner": "Conner is a town in Apayao, offering stunning views of the Apayao river.",
            },
            "Benguet": {
                "La Trinidad": "La Trinidad is the capital of Benguet, famous for its scenic strawberry farms.",
            },
            "Ifugao": {
                "Lagawe": "Lagawe is the capital municipality of Ifugao, known for the Banaue Rice Terraces.",
            },
            "Kalinga": {
                "Tabuk": "Tabuk is the capital of Kalinga, a province known for its vibrant indigenous culture.",
            },
            "Mountain Province": {
                "Bontoc": "Bontoc is the capital of Mountain Province, with historical significance and beautiful views.",
            }
        }
        return descriptions.get(province, {}).get(municipality, "No information available for this selection.")


    def search_loc(self):
        search_query = self.search_bar.text()
        if search_query:
            print(f"Searching for: {search_query}")
            folium.Marker([45.5236, -122.6750], popup=f"Search: {search_query}").add_to(map)
            map.save(MAP_PATH)
            
            self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))

    def show_information_panel(self):
     # Information Panel
        self.scroll_container = QScrollArea(self)
        self.scroll_container.setGeometry(950, 150, 490, 600)
        self.scroll_container.setWidgetResizable(True)
        self.scroll_container.setStyleSheet("""
            border: none;
            border-radius: 8px;
            background-color: #f2efe9;
        """)
        self.info_panel = QWidget()
        self.info_panel.setStyleSheet("background-color: #f2efe9; border-radius: 8px;")
        self.scroll_container.setWidget(self.info_panel)
        info_layout = QVBoxLayout(self.info_panel)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(10)

        # Location Label
        self.location_category_label = QLabel("Location: Cordillera, Philippines", self.info_panel)
        self.location_category_label.setStyleSheet("font-size: 16px; color: #34495e;")
        info_layout.addWidget(self.location_category_label)

        # Separator
        separator_line = QFrame(self.info_panel)
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setStyleSheet("background-color: #000; margin-top: 2px; margin-bottom: 2px;")
        separator_line.setFixedHeight(1)
        info_layout.addWidget(separator_line)

        # Title
        self.main_category = QLabel("Cordillera Administrative Region", self.info_panel)
        self.main_category.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(self.main_category)

        # Main Category
        scroll_area = QScrollArea(self.info_panel)
        scroll_area.setFixedHeight(150)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.main_category_description = QLabel("""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque venenatis auctor ultrices. Nullam eget purus dignissim, commodo metus a, dictum mi. Pellentesque eleifend nulla velit, a viverra neque tincidunt at. Integer ac lobortis est, non rhoncus nunc. Cras nec finibus nisl. Etiam in vulputate elit. Aliquam erat volutpat. Vivamus nec cursus sem.Curabitur dictum vel orci sit amet auctor. Vivamus sapien neque, efficitur nec ante vel, interdum rhoncus felis. Aliquam cursus finibus ante, eu consectetur neque iaculis id. Proin auctor facilisis dolor a efficitur. Proin in leo ex. Suspendisse euismod metus ultricies nisl lobortis, non fringilla sapien mattis. Integer faucibus viverra dui. Vestibulum quis ultricies turpis. Maecenas sed sem lectus. Phasellus fringilla fermentum purus, ac interdum ipsum bibendum dignissim. Vestibulum imperdiet purus eros, posuere mollis magna feugiat id. Suspendisse at nisi vel erat semper rhoncus in sit amet neque. Aliquam vel lorem vitae felis semper pretium. Morbi venenatis fringilla varius. Pellentesque mattis, sem eu condimentum dapibus, enim odio lacinia enim, bibendum pharetra velit mi non neque.Morbi hendrerit, massa nec pretium pulvinar, enim diam sollicitudin risus, accumsan tincidunt dui leo pretium diam. Sed cursus libero sit amet neque consectetur dictum. Donec hendrerit ipsum id enim faucibus, at iaculis ipsum commodo. Donec et consectetur neque. Integer rhoncus orci justo, ac ornare urna aliquam in. Donec enim lacus, tristique ut nisl ac, varius tincidunt diam. Donec a dolor nec augue vehicula auctor.Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.Nunc vel imperdiet purus, eu auctor nisi. Nulla non odio vel quam cursus molestie. Sed ipsum nunc, suscipit ac lorem id, consequat elementum nunc. Morbi ut pharetra nunc, posueresuscipit elit. Vivamus eget sollicitudin felis, vel dictum velit. Nullam quis leo id elit mattis varius. Vestibulum ut justo aliquam, pharetra nibh vitae, venenatis urna. Aeneannec bibendum nibh.Vivamus turpis nisi, suscipit sit amet nulla eget, egestas auctor mi. Morbi convallis eleifend sagittis. Aenean dapibus cursus urna, id tincidunt lorem maximusat. Curabitur tempus metus id massa auctor rutrum. Etiam auctor sit amet lacus eget congue. Suspendisse potenti. Nulla odio mi, dictum eu gravida hendrerit, porta a diam. Craseu neque dictum, elementum metus a, ultricies orci. Morbi condimentum dictum enim eget laoreet. Proin vitae ante dictum, cursus lacus a, hendrerit augue. Praesent nec semper tortor. Vestibulum sodales odio et felis feugiat pulvinar.""", scroll_content)
        self.main_category_description.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        self.main_category_description.setWordWrap(True)
        self.main_category_description.setAlignment(Qt.AlignTop)
        scroll_layout.addWidget(self.main_category_description)
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        info_layout.addWidget(scroll_area)

        # About
        self.about_label = QLabel("About:", self.info_panel)
        self.about_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #34495e; padding-top: 5px;")
        info_layout.addWidget(self.about_label)
        self.about_description = QLabel("The Cordillera region is home to diverse indigenous communities and unique cultural heritage sites such as the Banaue Rice Terraces.", self.info_panel)
        self.about_description.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.about_description.setWordWrap(True)
        info_layout.addWidget(self.about_description)

        # Team
        self.team_label = QLabel("Team:", self.info_panel)
        self.team_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #34495e;")
        info_layout.addWidget(self.team_label)
        self.team_description = QLabel("""
            Alcaparas,
            Bromeo,
            Cagulada,
            Calsiman,
            Cendana,
            Galvan,
            Munar,
            """, self.info_panel)
        self.team_description.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.team_description.setWordWrap(True)
        info_layout.addWidget(self.team_description)

        # References
        self.references_label = QLabel("References:", self.info_panel)
        self.references_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #34495e;")
        info_layout.addWidget(self.references_label)
        self.references_description = QLabel("""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque venenatis auctor ultrices.
            """, self.info_panel)
        self.references_description.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.references_description.setWordWrap(True)
        info_layout.addWidget(self.references_description)

        # Set final layout
        self.info_panel.setLayout(info_layout)
        self.scroll_container.show()

cordimap = QApplication(sys.argv)
window = CordiMap()
window.show()

sys.exit(cordimap.exec_())
