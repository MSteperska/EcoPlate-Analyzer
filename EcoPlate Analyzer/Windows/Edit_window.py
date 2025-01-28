from PySide6.QtCore import (Qt, QTimer)
from PySide6.QtWidgets import (
    QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QComboBox,
    QCheckBox, QErrorMessage)

import app_state 
import Record


class EditWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EcoPlate Analyzer - Edit")
        self.setFixedSize(800, 450)

        self.appState = app_state.AppState.get_instance()
        self.bacteria_set = self.appState.bacteria_set
        self.stressor_set = self.appState.stressor_set
        self.concentration_set = self.appState.concentration_set
        self.time_set = self.appState.time_set
        self.repetition_set = self.appState.repetition_set
        self.filename = self.appState.filename_set

        self.records_dicts = self.appState.Records_dict
        self.all_records = self.appState.all_records

        self.selected_file = []
        self.selected_records = []

        self.ecoplate_labels = [[None for _ in range(13)] for _ in range(10)]       # matrix for ecoplate labels
        self.widgets_matrix = [[None for _ in range(6)] for _ in range(3)]          # matrix for ecoplate info input

        self.main_layout = QVBoxLayout()
        datasetSelection_layout = QHBoxLayout()
        ecoplate_layout = QGridLayout() 
        info_layout = QHBoxLayout()
        labels_panel = QVBoxLayout()       # info_layout left panel - labels for info panel
        info_panel = QGridLayout()         # info_layout right panel - info input panel
        button_layout = QHBoxLayout()

        # datasetSelection layout
        label = QLabel("Choose dataset:")
        self.combobox = QComboBox()
        self.combobox.setFixedWidth(380)
        self.combobox.addItems(self.filename)

        show_button = QPushButton("Show")
        show_button.setFixedWidth(150)
        show_button.clicked.connect(self.ShowButtonPushed)

        delete_button = QPushButton("Delete")
        delete_button.setFixedWidth(150)
        delete_button.clicked.connect(self.DeleteButtonPushed)      

        datasetSelection_layout.addWidget(label)
        datasetSelection_layout.addWidget(self.combobox)
        datasetSelection_layout.addWidget(show_button)
        datasetSelection_layout.addWidget(delete_button)

        # ecoplate layout
        letter_index = 0

        for x in range(0,13):
            for y in range(0,9):
                if x == 0 and y != 0:
                    letter = chr(65 + letter_index % 26)  
                    letter_index += 1 
                    label = QLabel(letter)
                    label.setAlignment(Qt.AlignCenter)
                    ecoplate_layout.addWidget(label, y, x)
                elif y == 0 and x != 0:
                    label = QLabel(str(x))
                    label.setAlignment(Qt.AlignCenter)
                    ecoplate_layout.addWidget(label, y, x)
                elif x == 0 and y == 0:
                    continue
                else:
                    label = QLabel("")
                    label.setAlignment(Qt.AlignCenter) 
                    ecoplate_layout.addWidget(label, y, x)
                    self.ecoplate_labels[y][x] = label
                    label.setStyleSheet("border: 1px solid rgba(0, 150, 136, 0.9);")


        # info layout
            # labels panel
        label_names = ["bacteria", "stressor", "concentration", "time", "blank", "repetition"]
        for x in range(0,6):
            label = QLabel(label_names[x])
            label.setAlignment(Qt.AlignRight)
            label.setFixedWidth(100)
            labels_panel.addWidget(label) 

            # info panel
        for x in range(0, 3):
            for y in range(0,6):
                if y == 4:
                    check_box = QCheckBox()
                    info_panel.addWidget(check_box, y, x) 
                    self.widgets_matrix[x][y] = check_box
                    check_box.checkStateChanged.connect(lambda _, col=x: self.ChangeLabelBackground(col))
                else:
                    box = QComboBox()
                    box.setEditable(True)
                    info_panel.addWidget(box, y, x)
                    self.widgets_matrix[x][y] = box
                    box.activated.connect(lambda _, col=x: self.ChangeLabelBackground(col))
                    box.currentTextChanged.connect(lambda _, col=x: self.ChangeLabelBackground(col))

        info_layout.addLayout(labels_panel)
        info_layout.addLayout(info_panel)

        # button layout
        update_button = QPushButton("Update")
        update_button.setFixedWidth(150)
        update_button.clicked.connect(self.UpdateButtonPushed) 
        button_layout.addStretch(1)
        button_layout.addWidget(update_button, alignment=Qt.AlignCenter)
        self.info_label = QLabel("")
        button_layout.addWidget(self.info_label)
        button_layout.addStretch(1)

        # main layout 
        self.main_layout.addLayout(datasetSelection_layout)
        self.main_layout.addLayout(ecoplate_layout)
        self.main_layout.addLayout(info_layout)
        self.main_layout.addLayout(button_layout)

        self.main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.main_layout)


    # FUNCTIONS

    def ShowButtonPushed(self):
        self.selected_file = self.combobox.currentText()
        self.selected_records = self.records_dicts.get('filename', {}).get(self.selected_file, [])

        if len(self.selected_records) != 3:
            QMessageBox.warning(self, "Error ", f"Exactly 3 records were not found for the file: {self.selected_file}")
            return

        for i in range(3):
            record = self.selected_records[i]
            self.DisplayData(i, record)

    def DeleteButtonPushed(self):
        record_count = len(self.all_records)
        self.DeleteData()
        self.DeleteFromCombobox()
        self.UpdateSets()
        if(record_count - 3 == len(self.all_records)):
            self.Success_message("Records deleted successfully!")


    def UpdateButtonPushed(self):
        if not self.Validate_input():
            return 
        record_count = len(self.all_records)
        self.DeleteData()
        self.AddNewRecord()
        self.UpdateSets()

        if(record_count == len(self.all_records)):
            self.Success_message("Records edited successfully!")


    def DisplayData(self, row, record):
        self.widgets_matrix[row][0].setCurrentText(record.bacteria)
        self.widgets_matrix[row][1].setCurrentText(record.stressor)
        self.widgets_matrix[row][2].setCurrentText(record.concentration)
        self.widgets_matrix[row][3].setCurrentText(record.time)
        self.widgets_matrix[row][4].setChecked(record.blank)
        self.widgets_matrix[row][5].setCurrentText(record.repetition)

        ecoplate_data = record.ecoplate

        start_col = row * 4
        end_col = start_col + 4

        for i in range(1, 9):
            for j in range(start_col + 1, end_col + 1):
                value = ecoplate_data[i - 1][j - (start_col + 1)]
                self.ecoplate_labels[i][j].setText(str(value))

    def DeleteData(self):
        records_to_remove = self.selected_records

        for record_to_remove in records_to_remove:
            for key, sub_dict in list(self.records_dicts.items()):  # copy of keys in lists
                for sub_key, records in list(sub_dict.items()):  # copy of subkeys
                    self.records_dicts[key][sub_key] = [record for record in records if id(record) != id(record_to_remove)]

                    # delete subkey if subkey's list empty
                    if not self.records_dicts[key][sub_key]:
                        del self.records_dicts[key][sub_key]

        records_to_remove = [record for record in self.all_records if record.file_name == self.selected_file]
        for record in records_to_remove:
            self.all_records.remove(record)


    def DeleteFromCombobox(self):

        # deleting combobox option
        index = self.combobox.findText(self.selected_file)
        if index != -1:
            self.combobox.removeItem(index)

        # deleting filname from filename set
        if self.selected_file in self.filename:
            self.filename.remove(self.selected_file)


    def UpdateSets(self):
        
        self.bacteria_set.clear()
        self.stressor_set.clear()
        self.concentration_set.clear()
        self.time_set.clear()
        self.repetition_set.clear()

        for key, sub_dict in self.records_dicts.items():  
            for sub_key, records in sub_dict.items(): 
                for record in records:
                    # sets update
                    self.bacteria_set.add(record.bacteria)
                    self.stressor_set.add(record.stressor)
                    self.concentration_set.add(record.concentration)
                    self.time_set.add(record.time)
                    self.repetition_set.add(record.repetition)


    def AddNewRecord(self):
        
        for index in range(3):  # creating 3 new records
            
            bacteria = self.widgets_matrix[index][0].currentText()
            stressor = self.widgets_matrix[index][1].currentText()
            concentration = self.widgets_matrix[index][2].currentText()
            time = self.widgets_matrix[index][3].currentText()
            blank = self.widgets_matrix[index][4].isChecked()
            repetition = self.widgets_matrix[index][5].currentText()
            file_name = self.combobox.currentText()

            ecoplate_values = []
            start_col = index * 4
            end_col = start_col + 4

            for i in range(2, 10):
                row_values = []
                for j in range(start_col+2, end_col+2):
                    row_values.append(self.ecoplate_labels[i-1][j-1].text())
                ecoplate_values.append(row_values)

                # creating a new record of data
            newRecord = Record.EcoplateExperimentRecord(
                bacteria, stressor, concentration, time, blank, repetition, ecoplate_values, file_name)
            self.appState.all_records.append(newRecord)

                # adding values to combobox lists
            if bacteria not in [self.widgets_matrix[index][0].itemText(i) for i in range(self.widgets_matrix[index][0].count())]:
                self.widgets_matrix[index][0].addItem(bacteria)
            if stressor not in [self.widgets_matrix[index][1].itemText(i) for i in range(self.widgets_matrix[index][1].count())]:
                self.widgets_matrix[index][1].addItem(stressor)
            if concentration not in [self.widgets_matrix[index][2].itemText(i) for i in range(self.widgets_matrix[index][2].count())]:
                self.widgets_matrix[index][2].addItem(concentration)
            if time not in [self.widgets_matrix[index][3].itemText(i) for i in range(self.widgets_matrix[index][3].count())]:
                self.widgets_matrix[index][3].addItem(time)
            if repetition not in [self.widgets_matrix[index][5].itemText(i) for i in range(self.widgets_matrix[index][5].count())]:
                self.widgets_matrix[index][5].addItem(repetition)
                
                # adding record to dicts
            self.appState.Records_dict['bacteria'].setdefault(newRecord.bacteria, []).append(newRecord)
            self.appState.Records_dict['stressor'].setdefault(newRecord.stressor, []).append(newRecord)
            self.appState.Records_dict['concentration'].setdefault(newRecord.concentration, []).append(newRecord)
            self.appState.Records_dict['time'].setdefault(newRecord.time, []).append(newRecord)
            self.appState.Records_dict['blank'].setdefault(newRecord.blank, []).append(newRecord)
            self.appState.Records_dict['repetition'].setdefault(newRecord.repetition, []).append(newRecord)
            self.appState.Records_dict.setdefault('filename', {}).setdefault(newRecord.file_name, []).append(newRecord)
            self.appState.filename_set.add(file_name)

    
    def ChangeLabelBackground(self, col):
        col_start = col * 4 + 1
        col_end = col_start + 4

        # reset all backgrounds
        for r in range(1, 13):
            for c in range(1, 9):
                if self.ecoplate_labels[c][r] is not None:
                    self.ecoplate_labels[c][r].setStyleSheet("background-color: None; border: 1px solid rgba(0, 150, 136, 0.9);")
                else:
                    print(f"Error: QLabel at ({c}, {r}) is None!")
        
        # Highlight specific cells in the given column group
        for r in range(col_start, col_end):
            for c in range(1, 9): 
                if self.ecoplate_labels[c][r] is not None:  
                    self.ecoplate_labels[c][r].setStyleSheet("background-color: rgba(0, 150, 136, 0.2); border: 1px solid rgba(0, 150, 136, 0.9);")
                else:
                    print(f"Error: QLabel at ({c}, {r}) is None!")

    def Success_message(self, text):
        self.timer = QTimer(self)
        self.timer.setInterval(3000)  
        self.info_label.setText(text)
        self.timer.timeout.connect(lambda: self.info_label.setText(""))
        self.timer.start()

    def Validate_input(self):
        for col in range(3):
            # bacteria 
            if not self.widgets_matrix[col][0].currentText():
                self.show_error("Fill in the bacteria info.")
                return False
            
            # stressor
            if not self.widgets_matrix[col][1].currentText():
                self.show_error("Fill in the stressor info.")
                return False

            # concentration
            try:
                concentration_value = float(self.widgets_matrix[col][2].currentText())
                if concentration_value <= 0:
                    self.show_error("Concentration must be more than 0.")
                    return False
            except ValueError:
                self.show_error("Concentration must be a number.")
                return False

            # time  
            try:
                time_value = int(self.widgets_matrix[col][3].currentText())
                if time_value < 0:
                    self.show_error("Time must be at least 0.")
                    return False
            except ValueError:
                self.show_error("Time must be a number.")
                return False
            
            # repetition
            try:
                rep_value = int(self.widgets_matrix[col][5].currentText())
                if rep_value < 0:
                    self.show_error("Repetiton must be at least 0.")
                    return False
            except ValueError:
                self.show_error("Repetition must be a number.")
                return False
            
        return True
    
    def show_error(self, message):
        QMessageBox.warning(self, "ERROR", message)

