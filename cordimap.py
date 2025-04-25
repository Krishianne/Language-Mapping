import sys
import os 
import folium
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QCompleter
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
        self.search_bar.setPlaceholderText("Search for languages/dialects...")
        self.search_bar.setFixedHeight(30)
        self.search_bar.setStyleSheet("padding: 5px; font-size: 12px; border: none;")

        # Add completer for suggestions
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.search_bar.setCompleter(self.completer)

        # Connect text changed signal to update suggestions
        self.search_bar.textChanged.connect(self.update_suggestions)

        self.search_btn = QPushButton("SEARCH")
        self.search_btn.setFixedSize(80, 30)
        self.search_btn.setStyleSheet("font-size: 12px; border: none;")

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_btn)

        self.municipalities.currentIndexChanged.connect(self.selected_province_municipality)
        self.search_btn.clicked.connect(self.search_loc)
        # Add return pressed event
        self.search_bar.returnPressed.connect(self.search_loc)

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
            self.load_municipalities(selected_province)
            self.clear_province_btn.show()  # Make sure the clear button is visible
            self.municipalities.setEnabled(True)  # Enable the dropdown
            if hasattr(self, 'province_scroll_container'):
                self.province_scroll_container.show()  # Show the scroll container

    def load_municipalities(self, province):
        self.province_marker(province)

        municipalities = self.get_municipalities(province)
        print(f"Municipalities for {province}: {municipalities}")  # Debugging line

        self.municipalities.addItem('Select Municipality')
        self.municipalities.setItemData(0, 0, Qt.UserRole - 1)
        self.municipalities.addItems(municipalities)

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
        self.dynamic_location.setStyleSheet("font-size: 13px; font-weight: bold; color: #34495e; text-transform: none;")
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

        dynamic_description = self.get_dynamic_description(province, municipality)

        # Add the table widget directly to the layout
        dynamic_info_layout.addWidget(dynamic_description)

        # Only add language-related details if municipality is provided
        if municipality:
            self.dynamic_language_info_widget = self.get_dynamic_municipality(province, municipality)
            dynamic_info_layout.addWidget(self.dynamic_language_info_widget)

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
                QMessageBox.information(self, "Search", "Please enter a language to search.")
                return

            # Hide other panels if visible
            for panel_name in ["scroll_container", "dynamic_scroll_container", "province_scroll_container"]:
                if hasattr(self, panel_name):
                    panel = getattr(self, panel_name)
                    if panel.isVisible():
                        panel.hide()

            # Step 1: Get language_id
            language_id = self.get_language_id(search_query)
            if not language_id:
                self.search_scroll_panel(search_query, None)
                return

            # Step 2: Get most relevant location
            location_result = self.get_highest_percentage_location(language_id)
            if location_result:
                location_type, province_name, municipality_name, percentage = location_result
                self.search_scroll_panel(search_query, {
                    'language_id': language_id,
                    'location_type': location_type,
                    'province_name': province_name,
                    'municipality_name': municipality_name,
                    'percentage': percentage
                })
            else:
                self.search_scroll_panel(search_query, None)

        except Exception as e:
            print(f"Error in search_loc(): {e}")
            QMessageBox.warning(self, "Search Error", f"Failed to process search: {e}")

    def search_scroll_panel(self, query, location_data):
        if hasattr(self, 'search_scroll_container'):
            self.search_scroll_container.deleteLater()

        self.search_scroll_container = QScrollArea(self)
        self.search_scroll_container.setGeometry(950, 150, 490, 600)
        self.search_scroll_container.setWidgetResizable(True)
        self.search_scroll_container.setStyleSheet("""
            border: 2px solid #B4B6C4;
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
        search_layout.setSpacing(10)

        if not location_data:
        # No results found case
            no_results = QLabel(f"No language/dialect results found for '{query}'")
            no_results.setStyleSheet("font-size: 16px; color: #34495e;")
            search_layout.addWidget(no_results)
            self.search_scroll_container.show()
            return

        # Determine the correct coordinates based on location type
        if location_data['location_type'] == 'municipality':
            # For municipality results
            municipality_name = location_data['municipality_name'].capitalize()
            province_name = location_data['province_name'].capitalize()
            
            # Use municipality coordinates if available, otherwise use province marker coords
            if municipality_name in self.muni_coords:
                coords = self.muni_coords[municipality_name]
                self.base_map(location=coords, zoom=10)
                folium.Marker(coords, popup=municipality_name).add_to(self.map)
            else:
                # Fall back to province marker if municipality coords not available
                self.province_marker(province_name)
                coords = self.marker_coords[province_name]
            
            location_text = f"{municipality_name}, {province_name}"
        else:
            # For province results, use the province_marker method
            province_name = location_data['province_name'].capitalize()
            self.province_marker(province_name)
            coords = self.marker_coords[province_name]
            location_text = province_name

        # Save and refresh the map
        self.map.save(MAP_PATH)
        self.browser.setUrl(QUrl.fromLocalFile(MAP_PATH))

        # Display location information
        location_label = QLabel(f"Location: {location_text} ({coords[0]}, {coords[1]})")
        location_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #34495e;")
        search_layout.addWidget(location_label)

        # Separator
        separator_line = QFrame(search_panel)
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setStyleSheet("background-color: #000;")
        separator_line.setFixedHeight(1)
        search_layout.addWidget(separator_line)

        # Searched word
        searched_word = QLabel(f"{query}")
        searched_word.setStyleSheet("font-size: 20px; font-weight: bold; color: #34495e;")
        search_layout.addWidget(searched_word)

        search_description = QLabel(f"Showing results for '{query}'.", search_panel)
        search_description.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        search_description.setWordWrap(True)
        search_layout.addWidget(search_description)

        # Places with same language
        same_language_label = QLabel("Places with the Same Language/Dialect")
        same_language_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495e; padding-top: 10px;")
        search_layout.addWidget(same_language_label)

        # Get places with same language
        same_language_places = self.get_same_language_places(location_data)
        same_language_text = QLabel(same_language_places)
        same_language_text.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        same_language_text.setWordWrap(True)
        search_layout.addWidget(same_language_text)

        # Common Phrases Translation
        phrases_label = QLabel("Common Phrases Translation")
        phrases_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495e; padding-top: 10px;")
        search_layout.addWidget(phrases_label)

        # Get common phrases table
        phrases_table = self.get_common_phrases_table(location_data['language_id'])
        search_layout.addWidget(phrases_table)

        # Set layout and show
        search_panel.setLayout(search_layout)
        self.search_scroll_container.show()

    def get_same_language_places(self, location_data):
        try:
            language_id = location_data['language_id']
            places = []

            if location_data['location_type'] == 'province':
                # Get other provinces with this language
                self.cur.execute("""
                    SELECT p.province_name
                    FROM province_languages pl
                    JOIN provinces p ON pl.province_id = p.province_id
                    WHERE pl.language_id = %s
                    AND p.province_name != %s
                    ORDER BY pl.percentage_value DESC
                    LIMIT 5;
                """, (language_id, self.format_location_name(location_data['province_name'])))
                results = self.cur.fetchall()
                places = [self.format_location_name(result[0]) for result in results]
            else:
                # Get other municipalities in same province with this language
                self.cur.execute("""
                    SELECT m.municipality_name
                    FROM municipality_languages ml
                    JOIN municipalities m ON ml.municipality_id = m.municipality_id
                    JOIN provinces p ON m.province_id = p.province_id
                    WHERE ml.language_id = %s
                    AND p.province_name = %s
                    AND m.municipality_name != %s
                    ORDER BY ml.percentage_value DESC
                    LIMIT 5;
                """, (language_id, self.format_location_name(location_data['province_name']), self.format_location_name(location_data['municipality_name'])))
                results = self.cur.fetchall()
                places = [f"{self.format_location_name(result[0])}, {self.format_location_name(location_data['province_name'])}" for result in results]

            if not places:
                return "No other places found with this language."
            
            return "\n".join(places)
        except Exception as e:
            print(f"Error getting same language places: {e}")
            return "Error loading places with same language."

    def get_common_phrases_table(self, language_id):
        """Create a table widget for common phrases."""
        table_widget = QTableWidget()
        
        try:
            self.cur.execute("""
                SELECT language_phrase, english_phrase
                FROM phrases
                WHERE language_id = %s
                ORDER BY phrase_id
                LIMIT 5;
            """, (language_id,))
            phrases = self.cur.fetchall()

            if phrases:
                table_widget.setColumnCount(2)
                table_widget.setHorizontalHeaderLabels(['Language Phrase', 'English Translation'])
                table_widget.setRowCount(len(phrases))
                
                for row_idx, (lang_phrase, eng_phrase) in enumerate(phrases):
                    table_widget.setItem(row_idx, 0, QTableWidgetItem(lang_phrase))
                    table_widget.setItem(row_idx, 1, QTableWidgetItem(eng_phrase))
                
                table_widget.horizontalHeader().setStretchLastSection(True)
                table_widget.resizeColumnsToContents()
            else:
                table_widget.setRowCount(1)
                table_widget.setColumnCount(1)
                table_widget.setItem(0, 0, QTableWidgetItem("No common phrases found."))
                
        except Exception as e:
            print(f"Error getting common phrases: {e}")
            table_widget.setRowCount(1)
            table_widget.setColumnCount(1)
            table_widget.setItem(0, 0, QTableWidgetItem("Error loading phrases."))
        
        return table_widget

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
        self.location_category_label = QLabel("Location: ", self.info_panel)
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

    def get_dynamic_description(self, province, municipality=None):
        """Get description and details from the database for municipalities in the selected province."""
        # Create a QTableWidget for displaying results
        table_widget = QTableWidget()

        try:
            # If a municipality is provided, adjust the query to filter by municipality as well
            if municipality:
                query = """
                    SELECT 
                        ld.language_name, 
                        ml.percentage_value
                    FROM municipality_languages ml
                    JOIN languages_dialects ld ON ml.language_id = ld.language_id
                    JOIN municipalities m ON ml.municipality_id = m.municipality_id
                    JOIN provinces p ON m.province_id = p.province_id
                    WHERE LOWER(m.municipality_name) = LOWER(%s)
                    AND LOWER(p.province_name) = LOWER(%s)
                    ORDER BY ml.percentage_value DESC
                    LIMIT 3;
                """
                self.cur.execute(query, (municipality, province))
            else:
                # Default query to fetch language information for the entire province
                query = """
                    SELECT 
                        ld.language_name, 
                        pl.percentage_value
                    FROM province_languages pl
                    JOIN languages_dialects ld ON pl.language_id = ld.language_id
                    JOIN provinces p ON pl.province_id = p.province_id
                    WHERE LOWER(p.province_name) = LOWER(%s)
                    ORDER BY pl.percentage_value DESC
                    LIMIT 3;
                """
                self.cur.execute(query, (province,))

            rows = self.cur.fetchall()

            if rows:
                # Set up the table format based on whether a municipality is selected or not
                if municipality:
                    # For selected municipality, show only language name and percentage
                    table_widget.setColumnCount(2)
                    table_widget.setHorizontalHeaderLabels(['Language Name', 'Percentage'])
                    table_widget.setRowCount(len(rows))
                    
                    for row_index, row in enumerate(rows):
                        language, percentage = row
                        table_widget.setItem(row_index, 0, QTableWidgetItem(language))
                        table_widget.setItem(row_index, 1, QTableWidgetItem(f"{percentage}%"))
                else:
                    # For the entire province, language name, and percentage
                    table_widget.setColumnCount(2)
                    table_widget.setHorizontalHeaderLabels(['Language Name', 'Percentage'])
                    table_widget.setRowCount(len(rows))
                    
                    for row_index, row in enumerate(rows):
                        language, percentage = row
                        table_widget.setItem(row_index, 0, QTableWidgetItem(language))
                        table_widget.setItem(row_index, 1, QTableWidgetItem(f"{percentage}%"))
            else:
                # If no data is found, display a message
                table_widget.setRowCount(1)
                table_widget.setColumnCount(1)
                table_widget.setHorizontalHeaderLabels(['No Information Available'])
                table_widget.setItem(0, 0, QTableWidgetItem(f"No information available for {municipality or province}"))

        except Exception as e:
            print(f"Database error: {e}")
            # In case of error, show an error message
            table_widget.setRowCount(1)
            table_widget.setColumnCount(1)
            table_widget.setHorizontalHeaderLabels(['Error'])
            table_widget.setItem(0, 0, QTableWidgetItem("Error fetching data"))

        return table_widget

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
            
            return info or "No information available."

        except Exception as e:
            print(f"Database error: {e}")
            return "No information available."
    
    def get_municipalities(self, province):
        try:
            query = """
                SELECT municipality_name
                FROM municipalities
                JOIN provinces USING (province_id)
                WHERE province_name = %s
                ORDER BY municipality_name;
            """ 
            self.cur.execute(query, (province,))
            rows = self.cur.fetchall()
            return [self.format_location_name(row[0]).title() for row in rows]
        except Exception as e:
            print(f"SQL error fetching municipalities: {e}")
        return []
    
    def get_dynamic_municipality(self, province, municipality):
        """Create a table widget to display the language phrases and English phrases for the selected municipality."""
        # Create a new QTableWidget
        table_widget = QTableWidget()

        try:
            # Query to fetch language phrases and their English equivalents for the selected municipality
            query = """
                WITH top_languages AS (
                    SELECT 
                        ld.language_id,
                        ld.language_name, 
                        ml.percentage_value
                    FROM municipality_languages ml
                    JOIN languages_dialects ld ON ml.language_id = ld.language_id
                    JOIN municipalities m ON ml.municipality_id = m.municipality_id
                    JOIN provinces p ON m.province_id = p.province_id
                    WHERE LOWER(m.municipality_name) = LOWER(%s)
                    AND LOWER(p.province_name) = LOWER(%s)
                    ORDER BY ml.percentage_value DESC
                    LIMIT 3
                )
                SELECT 
                    tl.language_name, 
                    p.language_phrase, 
                    p.english_phrase
                FROM phrases p
                JOIN top_languages tl ON p.language_id = tl.language_id
                ORDER BY tl.language_name;
            """
            self.cur.execute(query, (municipality, province))
            rows = self.cur.fetchall()

            if rows:
                # Set the number of columns based on the result
                table_widget.setColumnCount(3)  # Language Name | Language Phrase | English Phrase
                table_widget.setHorizontalHeaderLabels(['Language Name', 'Language Phrase', 'English Phrase'])

                # Set the number of rows based on the fetched data
                table_widget.setRowCount(len(rows))

                for row_index, row in enumerate(rows):
                    language, phrase, english_phrase = row
                    table_widget.setItem(row_index, 0, QTableWidgetItem(language))
                    table_widget.setItem(row_index, 1, QTableWidgetItem(phrase))
                    table_widget.setItem(row_index, 2, QTableWidgetItem(english_phrase))
            else:
                # If no phrases are found, show a message indicating no data
                table_widget.setRowCount(1)
                table_widget.setColumnCount(1)
                table_widget.setHorizontalHeaderLabels(['No Information Available'])
                table_widget.setItem(0, 0, QTableWidgetItem(f"No phrases found for {municipality}"))

        except Exception as e:
            print(f"Error fetching phrases: {e}")
            # In case of error, show an error message
            table_widget.setRowCount(1)
            table_widget.setColumnCount(1)
            table_widget.setHorizontalHeaderLabels(['Error'])
            table_widget.setItem(0, 0, QTableWidgetItem("Error fetching data"))

        return table_widget

    def get_language_suggestions(self, query):
        """Fetch language suggestions from the database based on user input."""
        try:
            query = f"%{query}%"
            sql = """
                SELECT language_name 
                FROM languages_dialects 
                WHERE LOWER(language_name) LIKE LOWER(%s)
                LIMIT 10;
            """
            self.cur.execute(sql, (query,))
            return [row[0] for row in self.cur.fetchall()]
        except Exception as e:
            print(f"Error fetching suggestions: {e}")
            return []
    
    def update_suggestions(self):
        """Update the suggestions as the user types."""
        query = self.search_bar.text().strip()
        if query:
            suggestions = self.get_language_suggestions(query)
            model = QStringListModel()
            model.setStringList(suggestions)
            self.completer.setModel(model)
        else:
            # Clear suggestions if search bar is empty
            self.completer.setModel(QStringListModel())

    def select_municipality_and_show_info(self, municipality):
        """Select the municipality in the dropdown and show its information."""
        municipality_index = self.municipalities.findText(municipality)
        if municipality_index >= 0:
            self.municipalities.setCurrentIndex(municipality_index)

    def get_language_id(self, language_name):
        try:
            self.cur.execute("""
                SELECT language_id FROM languages_dialects 
                WHERE LOWER(language_name) = LOWER(%s) LIMIT 1;
            """, (language_name,))
            result = self.cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error fetching language ID: {e}")
            return None

    def get_highest_percentage_location(self, language_id):
        try:
            self.cur.execute("""
                (SELECT 
                    'province' as type,
                    p.province_name as name,
                    NULL as municipality_name,
                    pl.percentage_value as percentage
                FROM province_languages pl
                JOIN provinces p ON pl.province_id = p.province_id
                WHERE pl.language_id = %s
                ORDER BY pl.percentage_value DESC
                LIMIT 1)
                
                UNION ALL
                
                (SELECT 
                    'municipality' as type,
                    p.province_name as name,
                    m.municipality_name,
                    ml.percentage_value as percentage
                FROM municipality_languages ml
                JOIN municipalities m ON ml.municipality_id = m.municipality_id
                JOIN provinces p ON m.province_id = p.province_id
                WHERE ml.language_id = %s
                ORDER BY ml.percentage_value DESC
                LIMIT 1)
                
                ORDER BY percentage DESC
                LIMIT 1;
            """, (language_id, language_id))
            return self.cur.fetchone()
        except Exception as e:
            print(f"Error fetching location with highest percentage: {e}")
            return None
    def format_location_name(self, name):
        return " ".join(word.capitalize() for word in name.strip().split())
      
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
