import sys
import os 
import folium
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap, QFont
from db import connect

# map = folium.Map(location=[16.9083, 122.3941], zoom_start=8, scrollWheelZoom=False, doubleClickZoom=False)
# # map = folium.Map(location=[16.9983, 122.3941], zoom_start=8,control_scale=False, scrollWheelZoom=False, zoomControl=False, doubleClickZoom=False)
# # folium.Marker([16.8691, 121.2199], popup="Click me!").add_to(map)
# # map.options['attributionControl'] = False

# map.save("map.html")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(BASE_DIR, "map.html")
LOGO_PATH = os.path.join(BASE_DIR, "cordilogo.png")

class CordiMap(QMainWindow):

    def __init__(self):
        super().__init__()

        self.conn = connect()  
        self.cur = self.conn.cursor()

        self.province_coords = {
            "Abra": [17.3289, 122.2739],
            "Apayao": [17.7291, 122.5999],
            "Benguet": [16.5642, 122.3090],
            "Ifugao": [16.8167, 122.6205],
            "Kalinga": [17.1897, 122.6898],
            "Mountain Province": [17.0956, 122.5580]
        }

        self.muni_coords = {
            "Calanasan": [18.2688, 121.0453],
            "Conner": [17.8141, 121.3216],
            "Flora": [18.2287, 121.4218],
            "Luna": [18.3444, 121.3723],
            "Kabugao": [18.0409, 121.1828],
            "Santa Marcela": [18.3058, 121.4364],
            "Pudtol": [18.2536, 121.3759]
        }

        self.marker_coords = {
            "Abra": [17.5891, 120.7899],
            "Apayao": [18.1500, 121.1966],
            "Benguet": [16.5842, 120.6899],
            "Ifugao": [16.8691, 121.2199],
            "Kalinga": [17.4591, 121.2899],
            "Mountain Province": [17.1391, 121.1099]
        }

        #sample
        self.municipalities_mapping = {
            "Abra": ["Bangued", "Lagayan", "Pilar", "San Isidro", "Tubo"],
            "Apayao": ["Calanasan", "Conner", "Flora", "Kabugao", "Luna", "Santa Marcela", "Pudtol"],
            "Benguet": ["La Trinidad", "Itogon", "Tuba", "Bokod", "Sablan"],
            "Ifugao": ["Lagawe", "Kiangan", "Lamut", "Hungduan", "Asipulo"],
            "Kalinga": ["Tabuk", "Pasil", "Lubuagan", "Rizal", "Pinukpuk"],
            "Mountain Province": ["Bontoc", "Sabangan", "Sagada", "Tadian", "Besao"]
        }

        self.setWindowTitle('CordiMap')
        self.setGeometry(0, 0, 1500, 800)
        
        self.browser = QWebEngineView()
        self.base_map()
        self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))
        self.setCentralWidget(self.browser)

        self.logo = QLabel(self)
        self.logo.setGeometry(50, 30, 200, 80) 
        logo = QPixmap(LOGO_PATH) 
        self.logo.setPixmap(logo.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setStyleSheet("background-color: transparent;")
        
        self.show_information_panel()
        self.header_panel()
    
    def base_map(self, location=None, zoom=8):
        if location is None:
            location = [16.9083, 122.3941]
        self.map = folium.Map(location=location, zoom_start=zoom, scrollWheelZoom=False, doubleClickZoom=False)
        self.map.save(MAP_PATH) 

    def header_panel(self):
        # --- Province Panel ---
        self.province_panel = QWidget(self)
        self.province_panel.setGeometry(950, 50, 240, 40)
        self.province_panel.setStyleSheet("background-color: #f2efe9; border-radius: 5px; border: 2px solid #B4B6C4;")

        province_layout = QHBoxLayout()
        province_layout.setContentsMargins(10, 5, 10, 5)

        self.provinces = QComboBox()
        self.provinces.setFixedHeight(30)
        self.provinces.addItems(["Select Province", "Abra", "Apayao", "Benguet", "Ifugao", "Kalinga", "Mountain Province"])
        self.provinces.setStyleSheet("""QComboBox { padding: 5px; font-size: 12px; background-color: transparent; border: none;}""")
        self.provinces.setItemData(0, 0, Qt.UserRole - 1)
        self.provinces.currentIndexChanged.connect(self.on_province_selected)

        province_layout.addWidget(self.provinces)

        self.clear_province_btn = QPushButton("clear")
        self.clear_province_btn.setFixedSize(30, 20)
        self.clear_province_btn.setStyleSheet("""
            QPushButton { border: none; color: red; font-size: 12px; background-color: transparent;}
            QPushButton::hover { color: darkred;}
        """)
        self.clear_province_btn.clicked.connect(self.clear_province_selection)
        self.clear_province_btn.hide()

        province_layout.addWidget(self.clear_province_btn)

        self.province_panel.setLayout(province_layout)

        # --- Municipality Panel ---
        self.municipality_panel = QWidget(self)
        self.municipality_panel.setGeometry(1200, 50, 240, 40)
        self.municipality_panel.setStyleSheet("background-color: #f2efe9; border-radius: 5px; border: 2px solid #B4B6C4;")

        municipality_layout = QHBoxLayout()
        municipality_layout.setContentsMargins(10, 5, 10, 5)

        self.municipalities = QComboBox()
        self.municipalities.setFixedHeight(30)
        self.municipalities.addItems(["Select Municipality"])
        self.municipalities.setStyleSheet("""QComboBox { padding: 5px; font-size: 12px; background-color: transparent; border: none;}""")
        self.municipalities.setEnabled(False) 
        self.municipalities.currentIndexChanged.connect(self.on_municipality_selected)

        municipality_layout.addWidget(self.municipalities)

        self.clear_municipality_btn = QPushButton("clear")
        self.clear_municipality_btn.setFixedSize(30, 20)
        self.clear_municipality_btn.setStyleSheet("""
            QPushButton { border: none; color: red; font-size: 12px; background-color: transparent;}
            QPushButton::hover { color: darkred;}
        """)
        self.clear_municipality_btn.clicked.connect(self.clear_municipality_selection)
        self.clear_municipality_btn.hide()

        municipality_layout.addWidget(self.clear_municipality_btn)

        self.municipality_panel.setLayout(municipality_layout)

        # --- Search Panel ---
        self.search_panel = QWidget(self)
        self.search_panel.setGeometry(950, 100, 490, 40)
        self.search_panel.setStyleSheet("background-color: #f2efe9; border-radius: 5px; border: 2px solid #B4B6C4;")

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 5, 10, 10)
        search_layout.setSpacing(5)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type here...")
        self.search_bar.setFixedHeight(30)
        self.search_bar.setStyleSheet("padding: 5px; font-size: 12px; border: none;")

        self.search_btn = QPushButton("SEARCH")
        self.search_btn.setFixedSize(80, 30)
        self.search_btn.setStyleSheet("font-size: 12px; border: none;")

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_btn)

        self.municipalities.currentIndexChanged.connect(self.selected_province_municipality)
        self.search_btn.clicked.connect(self.search_loc)

        self.search_panel.setLayout(search_layout)

    # Municipality disable/enable
    def on_province_selected(self, index):
        selected_province = self.provinces.currentText()

        self.municipalities.clear()

        if selected_province == "Select Province":
            
            self.municipalities.setEnabled(False)
            self.clear_province_btn.hide()
            if hasattr(self, 'province_scroll_container'):
                self.province_scroll_container.hide() 
        else:
            self.province_marker(selected_province)
            self.municipalities.setEnabled(True)
            municipalities_list = self.municipalities_mapping.get(selected_province, [])
            self.clear_province_btn.show()
            self.municipalities.addItems(['Select Municipality'])
            self.municipalities.setItemData(0, 0, Qt.UserRole - 1)
            self.municipalities.addItems(municipalities_list)

    def province_marker(self, province):
        coords = self.marker_coords[province]
        self.base_map(location=coords, zoom=8)  
        folium.Marker(coords, popup=province).add_to(self.map)
        self.map.save(MAP_PATH) 
        self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))

    def clear_province_selection(self):
        self.provinces.setCurrentIndex(0)
        self.base_map()
        self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))
        self.municipalities.clear()
        self.municipalities.addItem("Select Municipality")
        self.municipalities.setEnabled(False)
        self.clear_province_btn.hide()

    def on_municipality_selected(self, index):
        selected_municipality = self.municipalities.currentText()
        selected_province = self.provinces.currentText()

        if selected_municipality != "Select Municipality":
            self.remove_province_marker(selected_province)
            self.muni_marker(selected_municipality)

        if index == 0:  
            self.clear_municipality_btn.hide()
        else:
            self.clear_municipality_btn.show()

    def remove_province_marker(self, province):
        if province in self.marker_coords:
            self.base_map(location=self.marker_coords[province], zoom=8) 
        # coords = self.marker_coords[province]
        # folium.Marker(coords, popup=province).add_to(self.map)
        # self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))

    def muni_marker(self, municipality):
        coords = self.muni_coords.get(municipality)
        if coords:
            self.base_map(location=coords, zoom=10)
            folium.Marker(coords, popup=municipality).add_to(self.map)
            self.map.save(MAP_PATH)
            self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))

    def clear_municipality_selection(self):
        self.municipalities.setCurrentIndex(0)
        self.base_map()
        self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))
        self.clear_municipality_btn.hide()

        if hasattr(self, 'dynamic_scroll_container'):
            self.dynamic_scroll_container.hide()

    # Display selected province
    def selected_province_municipality(self, index):
        if self.provinces.currentIndex() != 0 and index != 0:
            province = self.provinces.currentText()
            municipality = self.municipalities.currentText()
            print(f"Province: {province}, Municipality: {municipality}")
            if hasattr(self, 'scroll_container') and self.scroll_container.isVisible():
                self.scroll_container.hide()
            if hasattr(self, 'search_scroll_container') and self.search_scroll_container.isVisible():
                self.search_scroll_container.hide()
            if hasattr(self, 'province_scroll_container') and self.province_scroll_container.isVisible():
                self.province_scroll_container.hide()
            self.create_dynamic_info_panel(province, municipality)

    # Provinces Panel
    def create_province_info_panel(self, province):
        if hasattr(self, 'province_scroll_container'):
            self.province_scroll_container.deleteLater()

        self.province_scroll_container = QScrollArea(self)
        self.province_scroll_container.setGeometry(950, 150, 490, 600)
        self.province_scroll_container.setWidgetResizable(True)
        self.province_scroll_container.setStyleSheet("border: none; border-radius: 8px; background-color: #f2efe9;")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        # Location Label
        coords = self.get_location(province)
        self.province_location_label = QLabel(f"Location: {province} ({coords[0]}, {coords[1]})", self.info_panel)
        self.province_location_label.setStyleSheet("font-size: 13px; color: #34495e;")
        layout.addWidget(self.province_location_label)

        # Separator
        separator_line = QFrame(self.info_panel)
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setStyleSheet("background-color: #000; margin-top: 2px; margin-bottom: 2px;")
        layout.addWidget(separator_line)

        title = QLabel(f"{province} Information")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        description = QLabel(f"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ac scelerisque ex. Morbi luctus laoreet lacus ut congue. Aenean iaculis sagittis tellus viverra dignissim. Donec pellentesque lacinia vestibulum. Quisque id suscipit enim. Praesent nec nisl felis. Fusce rhoncus et risus non molestie. ")
        description.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignJustify)
        layout.addWidget(description)

        provinces = QLabel(f"Languages/Dialect Spoken")
        provinces.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(provinces)

        provinces_LorD_spoken = QLabel(f"""
            Lorem ipsum dolor sit amet
            Lorem ipsum dolor sit amet
            Lorem ipsum dolor sit amet
            """)
        provinces_LorD_spoken.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        provinces_LorD_spoken.setWordWrap(True)
        layout.addWidget(provinces_LorD_spoken)

        provinces_common_phrases = QLabel("Common Phrases")
        provinces_common_phrases.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(provinces_common_phrases)

        provinces_cp = QLabel(f""""
            Lorem ipsum dolor sit amet
            Lorem ipsum dolor sit amet
            Lorem ipsum dolor sit amet
            """)
        provinces_cp.setStyleSheet("font-size: 14px; color: #7f8c8d")
        provinces_cp.setWordWrap(True)
        layout.addWidget(provinces_cp)

        content.setLayout(layout)
        self.province_scroll_container.setWidget(content)
        self.province_scroll_container.show()

    # Province-Municipality Panel
    # TODO
    def create_dynamic_info_panel(self, province, municipality):
        self.dynamic_scroll_container = QScrollArea(self)
        self.dynamic_scroll_container.setGeometry(950, 150, 490, 600)
        self.dynamic_scroll_container.setWidgetResizable(True)
        self.dynamic_scroll_container.setStyleSheet("""
            border: 2px solid #B4B6C4;;
            border-radius: 8px;
            background-color: #f2efe9;
        """)

        self.dynamic_info_panel = QWidget()
        self.dynamic_info_panel.setStyleSheet("background-color: #f2efe9; border-radius: 8px;")
        self.dynamic_scroll_container.setWidget(self.dynamic_info_panel)

        dynamic_info_layout = QVBoxLayout(self.dynamic_info_panel)
        dynamic_info_layout.setContentsMargins(20, 20, 20, 20)
        dynamic_info_layout.setSpacing(5)

        coords = self.get_location(province)
        location_text = f"{province} ({coords[0]}, {coords[1]})"

        if municipality:  # Only add dash if municipality is provided
            location_text = f"{province} - {municipality} ({coords[0]}, {coords[1]})"

        self.dynamic_location = QLabel(f"Location: {location_text}", self.dynamic_info_panel)
        self.dynamic_location.setStyleSheet("font-size: 13px; font-weight: bold; color: #34495e;")
        dynamic_info_layout.addWidget(self.dynamic_location)

        separator_line = QFrame(self.dynamic_info_panel)
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setStyleSheet("background-color: #000; margin-top: 2px; margin-bottom: 2px;")
        separator_line.setFixedHeight(1)
        dynamic_info_layout.addWidget(separator_line)

        # Fetch dynamic info from the database
        dynamic_info = self.get_dynamic_info(province, municipality)

        # Format location string
        if municipality:
            location_text = f"{municipality}, {province}"
        else:
            location_text = f"{province}"

        # Combine title and info into one QLabel
        combined_text = f"<b style='font-size:16pt;'>{location_text} Information</b><br><span style='font-size:11pt; color:#7f8c8d;'>{dynamic_info}</span>"

        # Set the combined QLabel
        self.dynamic_info_label = QLabel(combined_text, self.dynamic_info_panel)
        self.dynamic_info_label.setStyleSheet("font-size: 13px; color: #34495e;")
        self.dynamic_info_label.setWordWrap(True)
        self.dynamic_info_label.setTextFormat(Qt.RichText)  
        dynamic_info_layout.addWidget(self.dynamic_info_label)

        self.dynamic_description_label = QLabel(self.get_dynamic_description(province, municipality), self.dynamic_info_panel)
        self.dynamic_description_label.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.dynamic_description_label.setWordWrap(True)
        dynamic_info_layout.addWidget(self.dynamic_description_label)

        self.dynamic_info_panel.setLayout(dynamic_info_layout)
        self.dynamic_scroll_container.show()

    def get_dynamic_description(self, province, municipality):
        """Get description from the database."""
        result = self.db.get_province_info(province)
        if result:
            return result[0]
        return f"No information available for {municipality}, {province}"

    # Search functionality
    def search_loc(self):
        try:
            search_query = self.search_bar.text().strip()
            if not search_query:
                print("Search query is empty.")  # Optional: Show a warning
                return  # Exit if no input

            # Ensure the map exists (create if missing)
            if not hasattr(self, 'map') or not self.map:
                self.map = folium.Map(location=[12.8797, 121.7740], zoom_start=6)  # Default: Philippines

            # Add a marker for the search query (replace with real coordinates)
            folium.Marker(
                location=[17.6, 121.7],  # Example: Apayao coordinates
                popup=f"Search: {search_query}"
            ).add_to(self.map)

            # Save and display the map
            self.map.save(MAP_PATH)
            self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))

            # Hide panels safely (check existence + visibility)
            for panel_name in ["scroll_container", "dynamic_scroll_container"]:
                if hasattr(self, panel_name):
                    panel = getattr(self, panel_name)
                    if panel.isVisible():
                        panel.hide()

            # Show search results
            self.search_scroll_panel(search_query)

        except Exception as e:
            print(f"Error in search_loc(): {e}")  # Log the error
            # Optional: Show a user-friendly warning (e.g., QMessageBox)
            QMessageBox.warning(self, "Search Error", f"Failed to process search: {e}")

    # Search Panel
    def search_scroll_panel(self, query):
        self.search_scroll_container = QScrollArea(self)
        self.search_scroll_container.setGeometry(950, 150, 490, 600)
        self.search_scroll_container.setWidgetResizable(True)
        self.search_scroll_container.setStyleSheet("""
            border: none;
            border-radius: 8px;
            background-color: #f2efe9;
        """)

        # Container widget inside scroll
        search_panel = QWidget()
        search_panel.setStyleSheet("background-color: #f2efe9; border-radius: 8px;")
        self.search_scroll_container.setWidget(search_panel)

        # Layout for the search panel
        search_layout = QVBoxLayout(search_panel)
        search_layout.setContentsMargins(20, 20, 20, 20)
        search_layout.setSpacing(2)
        search_location = QLabel(f"Location: ?")
        search_location.setStyleSheet("font-size: 16px; color: #34495e;")
        search_layout.addWidget(search_location)

        # Separator
        separator_line = QFrame(search_panel)
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setStyleSheet("background-color: #000;")
        separator_line.setFixedHeight(1)
        search_layout.addWidget(separator_line)

        # Searched word
        searched_word = QLabel(f"{query}", search_panel)
        searched_word.setStyleSheet("font-size: 20px; font-weight: bold; color: #34495e;")
        searched_word.setAlignment(Qt.AlignRight)
        search_layout.addWidget(searched_word)

        search_description = QLabel(f"Showing results for '{query}'.", search_panel)
        search_description.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        search_description.setWordWrap(True)
        search_layout.addWidget(search_description)

        search_similar_places = QLabel(f"Places with similar Language/Dialect")
        search_similar_places.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495e;")
        search_layout.addWidget(search_similar_places)

        search_places = QLabel(f"""
            Lorem ipsum dolor sit amet
            Lorem ipsum dolor sit amet
            Lorem ipsum dolor sit amet
        """)
        search_places.setStyleSheet("font-size: 16px; color: #34495e;")
        search_layout.addWidget(search_places)

        common_phrases_translation = QLabel("Common Phrases Translation")
        common_phrases_translation.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495e;")
        search_layout.addWidget(common_phrases_translation)

        # Apply layout and show the panel
        search_panel.setLayout(search_layout)
        self.search_scroll_container.show()        

    def show_information_panel(self):
     # Information Panel
        if hasattr(self, 'scroll_container'):
            self.scroll_container.deleteLater()
    
        self.scroll_container = QScrollArea(self)
        self.scroll_container.setGeometry(950, 150, 490, 600)
        self.scroll_container.setWidgetResizable(True)
        self.scroll_container.setStyleSheet("""
            border: 2px solid #B4B6C4;
            border-radius: 10px;
            background-color: #f2efe9;
        """)

        self.info_panel = QWidget()
        self.info_panel.setStyleSheet("background-color: #f2efe9; border-radius: 8px; border: none;")
        self.scroll_container.setWidget(self.info_panel)
        info_layout = QVBoxLayout(self.info_panel)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(10)

        # Location Label
        self.location_category_label = QLabel("Location: 16.9083, 122.3941", self.info_panel)
        self.location_category_label.setStyleSheet("font-size: 13px; color: #34495e;")
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
        self.main_category.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;  padding-top: 10px;")
        info_layout.addWidget(self.main_category)

        # Main Category
        self.main_category_description = QLabel("""Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.""", self.info_panel)
        self.main_category_description.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.main_category_description.setWordWrap(True)
        self.main_category_description.setAlignment(Qt.AlignJustify)
        info_layout.addWidget(self.main_category_description)

        # About
        self.about_label = QLabel("About:", self.info_panel)
        self.about_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #34495e; padding-top: 5px;")
        info_layout.addWidget(self.about_label)
        self.about_description = QLabel("The Cordillera region is home to diverse indigenous communities and unique cultural heritage sites such as the Banaue Rice Terraces.", self.info_panel)
        self.about_description.setStyleSheet("font-size: 13px; font-family: Tahoma; color: #7f8c8d;")
        self.about_description.setWordWrap(True)
        self.about_description.setAlignment(Qt.AlignJustify)
        info_layout.addWidget(self.about_description)

        # Team
        self.team_label = QLabel("Team:", self.info_panel)
        self.team_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #34495e; padding-top: 5px;")
        info_layout.addWidget(self.team_label)
        self.team_description = QLabel(
            'Alcaparras, Krishianne Mae\n'
            'Bromeo, Emmanuel Paolo\n'
            'Cagulada, Sheryn Ann\n'
            'Calsiman, Carl Allan\n'
            'Cendana, Juliana April\n'
            'Galvan, Marc Jansen\n'
            'Munar, Dulther Carlo',
            self.info_panel
        )
        self.team_description.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.team_description.setWordWrap(True)
        info_layout.addWidget(self.team_description)

        # References
        self.references_label = QLabel("References:", self.info_panel)
        self.references_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #34495e; padding-top: 5px;")
        info_layout.addWidget(self.references_label)
        self.references_description = QLabel(
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque venenatis auctor ultrices.', 
            self.info_panel)
        self.references_description.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        self.references_description.setWordWrap(True)
        info_layout.addWidget(self.references_description)

        # Set final layout
        self.info_panel.setLayout(info_layout)
        self.scroll_container.show()

    def get_dynamic_description(self, province, municipalities):
        """Get description and details from the database for municipalities in the selected province."""
        try:
            # SQL query to fetch municipality names, language names, and percentage values
            query = """
                SELECT m.municipality_name, ld.language_name, ml.percentage_value
                FROM municipalities m
                JOIN municipality_languages ml ON m.municipality_id = ml.municipality_id
                JOIN languages_dialects ld ON ml.language_id = ld.language_id
                JOIN provinces p ON m.province_id = p.province_id
                WHERE LOWER(p.province_name) = LOWER(%s)
                ORDER BY ml.percentage_value DESC;
            """
            # Execute the query with the selected province
            self.cur.execute(query, (province,))
            rows = self.cur.fetchall()

            if rows:
                # Create a table to display the results in a readable format
                table = "Municipality | Language Name | Percentage\n"
                table += "-" * 50 + "\n"
                for row in rows:
                    municipality, language, percentage = row
                    table += f"{municipality} | {language} | {percentage}%\n"
                return table
            else:
                return f"No information available for {province}."

        except Exception as e:
            print(f"Database error: {e}")
            return "No information available due to an error."

    def get_location(self, province):
        """
        Return the coordinates of the given province.
        If not found, return default coordinates.
        """
        return self.province_coords.get(province, [16.9083, 122.3941])  # Default Cordillera region center

    def get_dynamic_info(self, province, municipality):
        """Fetch dynamic information for the given province and municipality."""
        try:
            # Query to get the province information
            query_province = """
                SELECT information
                FROM provinces
                WHERE province_name = %s
                LIMIT 1;
            """
            self.cur.execute(query_province, (province,))
            province_info = self.cur.fetchone()

            # Query to get the municipality information
            query_municipality = """
                SELECT information
                FROM municipalities
                WHERE municipality_name = %s AND province_id = (
                    SELECT province_id FROM provinces WHERE province_name = %s LIMIT 1
                )
                LIMIT 1;
            """
            self.cur.execute(query_municipality, (municipality, province))
            municipality_info = self.cur.fetchone()

            # Combine both information if available
            info = ""
            if province_info:
                info += f"<b>Province Info:</b> {province_info[0]}<br>"
            if municipality_info:
                info += f"<b>Municipality Info:</b> {municipality_info[0]}<br>"

            # Optionally, you can add more info (languages, percentages, etc.) here.
            
            return info or "No information available."

        except Exception as e:
            print(f"Database error: {e}")
            return "No information available."

    def close(self):
        """Close the database connection."""
        self.cur.close()
        self.conn.close()

cordimap = QApplication(sys.argv)
font = QFont("Tahoma")
cordimap.setFont(font)
window = CordiMap()
window.show()

sys.exit(cordimap.exec_())
