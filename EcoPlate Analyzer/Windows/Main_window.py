#   main file for app
'''Windows initiation; 
    graphic and logical manipulation'''

# importing project files
import Record
import app_state
from Windows.Filter_window import FilterWindow
from Windows.Tests_window import TestsWindow
from Windows.Edit_window import EditWindow

import os
import pandas as pd
import numpy as np

from PySide6.QtCore import (Qt, QTimer)
from PySide6.QtWidgets import (

    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel,
    QComboBox, QCheckBox,
    QFileDialog, QMessageBox
)

#   ***********************

FILE_FILTERS = ["Microsoft Excel (*.xlsx)"]
ecoplate_labels = [[None for _ in range(13)] for _ in range(10)]       # matrix for ecoplate labels

def load_ecoplate_view(wave):
    for x in range(1, 13):
        for y in range(1, 9):
            label = ecoplate_labels[y][x]
            if label is not None:
                label.setText(str(wave.iloc[y - 1, x - 1]))  
            else:
                print(f"Error: QLabel at ({y}, {x}) is None!")


# Subclass QMainWindow to customize application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.file_name = None
        self.appState = app_state.AppState.get_instance()
        self.widgets_matrix = [[None for _ in range(6)] for _ in range(3)]       # matrix for comboboxes info panel

        self.setWindowTitle("EcoPlate Analyzer")
        self.setFixedSize(800, 400)

        main_layout = QVBoxLayout()
        upperPanel_layout = QHBoxLayout()
        bottomPanel_layout = QHBoxLayout()

        # upper panel
        buttonPanel_layout = QVBoxLayout()  # top left panel - buttons
        ecoplate_layout = QGridLayout()     # top right panel - ecoplate grid view

        #bottom panel
        labels_layout = QVBoxLayout()       # bottom left panel - labels for info panel
        info_layout = QGridLayout()         # bottom right panel - info input panel
        add_button = QPushButton("Add")     # the bottomest panel - add button
        add_button.setFixedWidth(150)
        add_button.clicked.connect(self.AddButtonPushed)
        self.info_label = QLabel("")       # label for successful adding message

        #loaded ecoplate view
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
                    ecoplate_labels[y][x] = label
                    label.setStyleSheet("border: 1px solid rgba(0, 150, 136, 0.9);")

        #   buttons panel
        button_LoadFile = QPushButton("Load File")
        button_LoadFile.clicked.connect(self.get_filename)

        button_Filter = QPushButton("Filter")
        button_Filter.clicked.connect(self.FilterButtonPushed)

        button_Edit = QPushButton("Edit")
        button_Edit.clicked.connect(self.EditButtonPushed)

        button_Tests = QPushButton("Tests")
        button_Tests.clicked.connect(self.TestsButtonPushed)

        button_LoadFile.setFixedWidth(200)
        button_Edit.setFixedWidth(200)
        button_Filter.setFixedWidth(200)
        button_Tests.setFixedWidth(200)

        buttonPanel_layout.addWidget(button_LoadFile)
        buttonPanel_layout.addWidget(button_Edit)
        buttonPanel_layout.addWidget(button_Filter)
        buttonPanel_layout.addWidget(button_Tests)

        #   info labels
        label_names = ["bacteria", "stressor", "concentration", "time", "blank", "repetition"]
        for x in range(0,6):
            label = QLabel(label_names[x])
            label.setAlignment(Qt.AlignRight)
            labels_layout.addWidget(label)        

        # info panel
        for x in range(0, 3):
            for y in range(0,6):
                if y == 4:
                    check_box = QCheckBox()
                    info_layout.addWidget(check_box, y, x) 
                    self.widgets_matrix[x][y] = check_box
                else:
                    box = QComboBox()                    
                    box.setEditable(True)
                    info_layout.addWidget(box, y, x)
                    self.widgets_matrix[x][y] = box
                    box.activated.connect(lambda _, col=x: self.ChangeLabelBackground(col))
                    box.currentTextChanged.connect(lambda _, col=x: self.ChangeLabelBackground(col))


        # setting up all layouts together
        
        upperPanel_layout.addLayout(buttonPanel_layout)
        upperPanel_layout.addLayout(ecoplate_layout)

        bottomPanel_layout.addLayout(labels_layout, stretch=1)
        bottomPanel_layout.addLayout(info_layout, stretch=3)

        main_layout.addLayout(upperPanel_layout)
        main_layout.addLayout(bottomPanel_layout)
        button_label_layout = QHBoxLayout()

        button_label_layout.addWidget(QWidget())
        button_label_layout.addWidget(QWidget())
        button_label_layout.addWidget(add_button)
        button_label_layout.addWidget(self.info_label)
        button_label_layout.addWidget(QWidget())

        main_layout.addLayout(button_label_layout)
        main_layout.setAlignment(Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)


# FUNCTIONS
            
    def get_filename(self):
        caption = "Open file"
        initial_dir = "" 
        dialog = QFileDialog()
        dialog.setWindowTitle(caption)
        dialog.setDirectory(initial_dir)
        dialog.setNameFilter("Excel Files (*.xlsx *xls)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]

            self.file_name = os.path.basename(file_path)

            wave_590 = pd.read_excel(file_path, usecols='B:M', skiprows=lambda x: x < 5 or x > 13)
            wave_720 = pd.read_excel(file_path, usecols='B:M', skiprows=lambda x: x < 18 or x > 26)
            wave = round((wave_590 - wave_720), 3)
            load_ecoplate_view(wave)

        else:
            self.show_error("No file has been chosen.")
            return None
   
    def AddButtonPushed(self):  

        if not self.file_name: 
            self.show_error("No file has been loaded. Please load a file first.")
            return 

        if not self.Validate_input():
            return    
        
        new_records = [] # list for 3 new records
        record_count_before = len(self.appState.all_records)

        for index in range(3):  # for every new record   

            # take input data
            bacteria = self.widgets_matrix[index][0].currentText()
            stressor = self.widgets_matrix[index][1].currentText()
            concentration = self.widgets_matrix[index][2].currentText()
            time = self.widgets_matrix[index][3].currentText()
            blank = self.widgets_matrix[index][4].isChecked()
            repetition = self.widgets_matrix[index][5].currentText()

            ecoplate_values = []
            start_col = index * 4
            end_col = start_col + 4

            for i in range(2, 10):
                row_values = []
                for j in range(start_col+2, end_col+2):
                        row_values.append(ecoplate_labels[i-1][j-1].text())
                ecoplate_values.append(row_values)

            # creating a new record of data
            newRecord = Record.EcoplateExperimentRecord(
                bacteria, stressor, concentration, time, blank, repetition, ecoplate_values, self.file_name)
            
            new_records.append(newRecord)

        # check if records in new_records are unique to each other
        for i in range(len(new_records)):
                for j in range(i + 1, len(new_records)):
                    if (new_records[i].bacteria == new_records[j].bacteria and
                        new_records[i].stressor == new_records[j].stressor and
                        new_records[i].concentration == new_records[j].concentration and
                        new_records[i].time == new_records[j].time and
                        new_records[i].repetition == new_records[j].repetition):
            
                        self.show_error("Duplicate records found among the three inputs. No records were added.")
                        return 

        # check if new records are not in data base yet
        for record in new_records:
                if self.record_exists(record):
                    self.show_error("One or more records already exist. No records were added.")
                    return

        for record in new_records:

            # chceck for duplicates without ecoplate atribute (in data base)
            for existing_record in self.appState.all_records:
                if (record.bacteria == existing_record.bacteria and
                    record.stressor == existing_record.stressor and
                    record.concentration == existing_record.concentration and
                    record.time == existing_record.time and
                    record.repetition == existing_record.repetition):
                    self.show_error("One or more records already exist. No records were added.")
                    return

            # check only ecoplate (in data base)
            if any(existing_record.ecoplate == record.ecoplate for existing_record in self.appState.all_records):
                self.show_error("One or more records already exist with the same ecoplate values. No records were added.")
                return

            # adding record to dicts
            self.appState.Records_dict['bacteria'].setdefault(record.bacteria, []).append(record)
            self.appState.Records_dict['stressor'].setdefault(record.stressor, []).append(record)
            self.appState.Records_dict['concentration'].setdefault(record.concentration, []).append(record)
            self.appState.Records_dict['time'].setdefault(record.time, []).append(record)
            self.appState.Records_dict['blank'].setdefault(record.blank, []).append(record)
            self.appState.Records_dict['repetition'].setdefault(record.repetition, []).append(record)
            self.appState.Records_dict.setdefault('filename', {}).setdefault(record.file_name, []).append(record)
            self.appState.filename_set.add(self.file_name)

            self.appState.all_records.append(record)

        # Adding values from comboboxes to sets
        for col_index in [0, 1, 2, 3, 5]:
            for row in self.widgets_matrix:
                combo_box = row[col_index]
                if isinstance(combo_box, QComboBox):
                    value = combo_box.currentText()
                    if col_index == 0:
                        self.appState.bacteria_set.add(value)
                    elif col_index == 1:
                        self.appState.stressor_set.add(value)
                    elif col_index == 2:
                        self.appState.concentration_set.add(value)
                    elif col_index == 3:
                        self.appState.time_set.add(value)
                    elif col_index == 5:
                        self.appState.repetition_set.add(value)

        #adding options to comboboxes
        for row in self.widgets_matrix:
            for col_index in [0, 1, 2, 3, 5]: 
                combo_box = row[col_index]
                if isinstance(combo_box, QComboBox):
                    combo_box.clear()
                    if col_index == 0:
                        # (bacteria_set)
                        for value in self.appState.bacteria_set:
                            if value not in [combo_box.itemText(i) for i in range(combo_box.count())]:
                                combo_box.addItem(value)
                    elif col_index == 1:
                        #  (stressor_set)
                        for value in self.appState.stressor_set:
                            combo_box.addItem(value)
                    elif col_index == 2:
                        #  (concentration_set)
                        for value in self.appState.concentration_set:
                            combo_box.addItem(value)
                    elif col_index == 3:
                        # (time_set)
                        for value in self.appState.time_set:
                            combo_box.addItem(value)
                    elif col_index == 5:
                        # (repetiton_set)
                        for value in self.appState.repetition_set:
                            combo_box.addItem(value)

        for row in self.widgets_matrix:
            for col_index in [0, 1, 2, 3, 5]: 
                combo_box = row[col_index]
                if isinstance(combo_box, QComboBox):
                    combo_box.setCurrentText("")

        # message
        if(record_count_before + 3 == len(self.appState.all_records)):
            self.info_label.setText("Records successfully added!")
            QTimer.singleShot(3000, self.clear_label_text)


    def clear_label_text(self):
        self.info_label.setText("")
    

    def FilterButtonPushed(self):
        self.filter_window = FilterWindow()
        self.filter_window.show()


    def TestsButtonPushed(self):
        self.tests_window = TestsWindow()
        self.tests_window.show()


    def EditButtonPushed(self):
        self.edit_window = EditWindow()
        self.edit_window.show()

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
                if concentration_value < 0:
                    self.show_error("Concentration must be at least 0.")
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
    
    def record_exists(self, new_record):
        for record in self.appState.all_records:
            if (record.bacteria == new_record.bacteria and
                record.stressor == new_record.stressor and
                record.concentration == new_record.concentration and
                record.time == new_record.time and
                record.blank == new_record.blank and
                record.repetition == new_record.repetition and
                record.file_name == new_record.file_name or
                np.array_equal(record.ecoplate, new_record.ecoplate)):
                return True
        return False


    def show_error(self, message):
        QMessageBox.warning(self, "ERROR", message)

    def ChangeLabelBackground(self, col):
        col_start = col * 4 + 1
        col_end = col_start + 4

        # reset all backgrounds
        for r in range(1, 13):
            for c in range(1, 9):
                if ecoplate_labels[c][r] is not None:
                    ecoplate_labels[c][r].setStyleSheet("background-color: None; border: 1px solid rgba(0, 150, 136, 0.9);")
                else:
                    print(f"Error: QLabel at ({c}, {r}) is None!")
        
        # Highlight specific cells in the given column group
        for r in range(col_start, col_end):
            for c in range(1, 9): 
                if ecoplate_labels[c][r] is not None: 
                    ecoplate_labels[c][r].setStyleSheet("background-color: rgba(0, 150, 136, 0.2); border: 1px solid rgba(0, 150, 136, 0.9);")
                else:
                    print(f"Error: QLabel at ({c}, {r}) is None!")


