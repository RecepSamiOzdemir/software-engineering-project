from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QMessageBox, QInputDialog, QDialog, QTextEdit
import sys
import pandas as pd
import matplotlib.pyplot as plt
from main import scrape_and_save
from PyQt5.QtCore import QThread, pyqtSignal

class FetchDataWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def run(self):
        try:
            # Veri çekme işlemini burada yapıyoruz
            self.log_signal.emit("Veri çekme işlemi başladı...\n")
            data_file = scrape_and_save()  # scrape_and_save fonksiyonunu çağırıyoruz
            self.log_signal.emit(f"Veri çekme işlemi tamamlandı: {data_file}")
            self.finished_signal.emit("Veri çekme işlemi başarıyla tamamlandı.")
        except Exception as e:
            self.log_signal.emit(f"Hata: {str(e)}")
            self.finished_signal.emit("Veri çekme işlemi başarısız oldu.")

class FetchDataDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veri Çekme İşlemi")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.close_button = QPushButton("Kapat")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

        self.worker = FetchDataWorker()
        self.worker.log_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def update_log(self, message):
        self.log_text.append(message)

    def on_finished(self, message):
        self.update_log(message)
        self.close_button.setEnabled(True)


def load_data():
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Brand", "Model", "Price", "Year", "Kilometer", "Color", "Province", "District", "Damage Information", "Sherry"])
    return df

def update_table(filtered_df, table_widget):
    # Filtrelenmiş verilerle tabloyu güncelleme
    table_widget.setRowCount(0)
    for index, row in filtered_df.iterrows():
        row_position = table_widget.rowCount()
        table_widget.insertRow(row_position)
        for col, value in enumerate(row):
            table_widget.setItem(row_position, col, QTableWidgetItem(str(value)))

def filter_data(data, brand, model, min_price, max_price, min_year, max_year, min_kilometer, max_kilometer, color, province, district, damage, sherry, table_widget):
    # Kullanıcıya göre verileri filtreleme
    filtered_df = data.copy()

    if brand:
        filtered_df = filtered_df[filtered_df["Brand"].str.contains(brand, case=False, na=False)]
    if model:
        filtered_df = filtered_df[filtered_df["Model"].str.contains(model, case=False, na=False)]
    if min_price and min_price.isdigit():
        filtered_df = filtered_df[filtered_df["Price"] >= float(min_price)]
    if max_price and max_price.isdigit():
        filtered_df = filtered_df[filtered_df["Price"] <= float(max_price)]
    if min_year and min_year.isdigit():
        filtered_df = filtered_df[filtered_df["Year"] >= int(min_year)]
    if max_year and max_year.isdigit():
        filtered_df = filtered_df[filtered_df["Year"] <= int(max_year)]
    if min_kilometer and min_kilometer.isdigit():
        filtered_df = filtered_df[filtered_df["Kilometer"] >= float(min_kilometer)]
    if max_kilometer and max_kilometer.isdigit():
        filtered_df = filtered_df[filtered_df["Kilometer"] <= float(max_kilometer)]
    if color:
        filtered_df = filtered_df[filtered_df["Color"].str.contains(color, case=False, na=False)]
    if province:
        filtered_df = filtered_df[filtered_df["Province"].str.contains(province, case=False, na=False)]
    if district:
        filtered_df = filtered_df[filtered_df["District"].str.contains(district, case=False, na=False)]
    if damage != "All":
        filtered_df = filtered_df[filtered_df["Damage Information"] == damage]

    update_table(filtered_df, table_widget)
    return filtered_df


def clear_filters(table_widget, *inputs):
    # Tüm filtreleri temizle ve tabloyu verisiz olarak yenile
    for input_widget in inputs:
        if isinstance(input_widget, QLineEdit):
            input_widget.clear()
        elif isinstance(input_widget, QComboBox):
            input_widget.setCurrentIndex(0)

    update_table(data, table_widget)

def plot_valuation_trends(filtered_df, group_by_attribute):
    # Filtrelenmiş verilerle değer trendlerini çizme
    if filtered_df.empty:
        QMessageBox.warning(None, "No Data", "No data matches the filters.")
        return

    if group_by_attribute not in filtered_df.columns:
        QMessageBox.warning(None, "Invalid Attribute", f"Attribute '{group_by_attribute}' not found in data.")
        return

    trend_data = filtered_df.groupby(group_by_attribute)["Price"].mean().reset_index()

    plt.figure(figsize=(10, 6))
    plt.bar(trend_data[group_by_attribute], trend_data["Price"], color="skyblue")
    plt.xlabel(group_by_attribute)
    plt.ylabel("Average Price")
    plt.title(f"Valuation Trends by {group_by_attribute}")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

class CarDataViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.data = load_data()
        self.filtered_data = self.data

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Car Data Viewer")
        self.setGeometry(100, 100, 1200, 700)

        layout = QVBoxLayout()

        filter_layout = QGridLayout()

        # Sütunlar için filtreleme
        self.brand_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Brand:"), 0, 0)
        filter_layout.addWidget(self.brand_entry, 0, 1)

        self.model_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Model:"), 0, 2)
        filter_layout.addWidget(self.model_entry, 0, 3)

        self.min_price_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Min Price:"), 1, 0)
        filter_layout.addWidget(self.min_price_entry, 1, 1)

        self.max_price_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Max Price:"), 1, 2)
        filter_layout.addWidget(self.max_price_entry, 1, 3)

        self.min_year_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Min Year:"), 2, 0)
        filter_layout.addWidget(self.min_year_entry, 2, 1)

        self.max_year_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Max Year:"), 2, 2)
        filter_layout.addWidget(self.max_year_entry, 2, 3)

        self.min_kilometer_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Min Kilometer:"), 3, 0)
        filter_layout.addWidget(self.min_kilometer_entry, 3, 1)

        self.max_kilometer_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Max Kilometer:"), 3, 2)
        filter_layout.addWidget(self.max_kilometer_entry, 3, 3)

        self.district_entry = QLineEdit()
        filter_layout.addWidget(QLabel("District:"), 4, 0)
        filter_layout.addWidget(self.district_entry, 4, 1)

        self.color_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Color:"), 4, 2)
        filter_layout.addWidget(self.color_entry, 4, 3)

        self.province_entry = QLineEdit()
        filter_layout.addWidget(QLabel("Province:"), 5, 0)
        filter_layout.addWidget(self.province_entry, 5, 1)

        self.damage_combobox = QComboBox()
        self.damage_combobox.addItems(
            [
                "All", "Without Tramer", "Badly damaged", "Unchanging", "Unpainted", "Unpainted-Unchanging", "Unpainted-Unchanging-Without Tramer"
            ]
        )
        filter_layout.addWidget(QLabel("Damage Report:"), 5, 2)
        filter_layout.addWidget(self.damage_combobox, 5, 3)

        layout.addLayout(filter_layout)

        button_layout = QHBoxLayout()

        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.apply_filters)
        button_layout.addWidget(self.filter_button)

        self.clear_button = QPushButton("Clear Filters")
        self.clear_button.clicked.connect(self.clear_filters)
        button_layout.addWidget(self.clear_button)

        self.show_graph_button = QPushButton("Show Valuation Trend Graph")
        self.show_graph_button.clicked.connect(self.show_graph)
        button_layout.addWidget(self.show_graph_button)

        self.scrape_button = QPushButton("Fetch Data")
        self.scrape_button.clicked.connect(self.fetch_data)
        button_layout.addWidget(self.scrape_button)

        layout.addLayout(button_layout)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.data.columns))
        self.table_widget.setHorizontalHeaderLabels(self.data.columns)
        layout.addWidget(self.table_widget)

        update_table(self.data, self.table_widget)

        self.setLayout(layout)

    def apply_filters(self):
        brand = self.brand_entry.text()
        model = self.model_entry.text()
        min_price = self.min_price_entry.text()
        max_price = self.max_price_entry.text()
        min_year = self.min_year_entry.text()
        max_year = self.max_year_entry.text()
        min_kilometer = self.min_kilometer_entry.text()
        max_kilometer = self.max_kilometer_entry.text()
        district = self.district_entry.text()
        color = self.color_entry.text()
        province = self.province_entry.text()
        damage = self.damage_combobox.currentText()

        self.filtered_data = filter_data(
            self.data, brand, model, min_price, max_price, min_year, max_year, min_kilometer, max_kilometer, color, province, district, damage, None, self.table_widget
        )

    def clear_filters(self):
        clear_filters(
            self.table_widget, self.brand_entry, self.model_entry, self.min_price_entry, self.max_price_entry,
            self.min_year_entry, self.max_year_entry, self.min_kilometer_entry, self.max_kilometer_entry,
            self.color_entry, self.province_entry, self.district_entry, self.damage_combobox
        )

    def show_graph(self):
        attribute = self.get_group_by_attribute()
        if attribute:
            plot_valuation_trends(self.filtered_data, attribute)

    def fetch_data(self):
        dialog = FetchDataDialog()
        dialog.exec_()  # Dialogu modal olarak açıyoruz

        # Veri çekme işlemi sonrası veriyi yükle ve tabloyu güncelle
        self.data = load_data()
        self.filtered_data = self.data
        update_table(self.data, self.table_widget)


    def get_group_by_attribute(self):
        items = ["Brand", "Model", "Year", "Kilometer", "Color", "Province", "District", "Damage Information"]
        attribute, ok = QInputDialog.getItem(self, "Select the Attribute to Group by", "Choose attribute:", items, 0, False)
        if ok:
            return attribute
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CarDataViewer()
    viewer.show()
    sys.exit(app.exec_())
