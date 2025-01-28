from PySide6.QtWidgets import (
    QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QListWidget, 
    QScrollArea, QFileDialog)

from itertools import product

import csv
import os
import app_state 
from RecordWidget import RecordWidget


class FilterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EcoPlate Analyzer - Filter")
        self.appState = app_state.AppState.get_instance() 

        self.saved_data = []        # container for all filtered data -> for .csv saving

        self.appState = app_state.AppState.get_instance()
        self.bacteria_set = self.appState.bacteria_set
        self.stressor_set = self.appState.stressor_set
        self.concentration_set = self.appState.concentration_set
        self.time_set = self.appState.time_set
        self.repetition_set = self.appState.repetition_set
        self.filename = self.appState.filename_set

        self.records_dicts = self.appState.Records_dict
        self.all_records = self.appState.all_records

        self.carbon_sources = self.appState.carbon_source_list
        self.carbon_sources_groups = self.appState.carbon_source_groups

        # layouts
        self.main_layout = QVBoxLayout()
        filetrsPanel_layout = QGridLayout()
        self.displayPanel_layout = QVBoxLayout()
        buttonsPanel_layout = QHBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(275)

        scroll_content_widget = QWidget()
        scroll_content_widget.setFixedWidth(500)
        scroll_content_widget.setLayout(self.displayPanel_layout)
        self.scroll_area.setWidget(scroll_content_widget)
        

        # filters panel
        label_names = ["bacteria", "stressor", "concentration", "time", "blank", "repetition", "carbon sources", "carbon sources groups"]
        self.list_widget = []    #listWidgets storage

        for col, label_text in enumerate(label_names):
            label = QLabel(label_text)
            filetrsPanel_layout.addWidget(label, 0 , col)
        for col in range(len(label_names)):
            self.listWidget = QListWidget()
            self.listWidget.setSelectionMode(QListWidget.MultiSelection)
            if col == 0:
                self.listWidget.addItems(sorted(self.bacteria_set))
            if col == 1:
                self.listWidget.addItems(sorted(self.stressor_set))
            elif col == 2:
                self.listWidget.addItems(sorted(self.concentration_set))
            elif col == 3:
                self.listWidget.addItems(sorted(self.time_set))
            elif col == 4:    # blank
                self.listWidget.addItems(["Yes", "No"])
            elif col == 5:
                self.listWidget.addItems(sorted(self.repetition_set))
            elif col == 6:
                carbon_sources_set = {item for sublist in self.carbon_sources for item in sublist}
                self.listWidget.addItems(carbon_sources_set)
            elif col == 7:
                self.listWidget.addItems(sorted(self.carbon_sources_groups))
            filetrsPanel_layout.addWidget(self.listWidget, 1, col)
            self.list_widget.append(self.listWidget)

            # Set column stretch proportions
        filetrsPanel_layout.setColumnStretch(0, 1.7)  # Bacteria
        filetrsPanel_layout.setColumnStretch(1, 1.7)  # Stressor
        filetrsPanel_layout.setColumnStretch(2, 1.2)  # Concentration
        filetrsPanel_layout.setColumnStretch(3, 1)  # Time
        filetrsPanel_layout.setColumnStretch(4, 1)  # Blank
        filetrsPanel_layout.setColumnStretch(5, 1.2)  # Repetition
        filetrsPanel_layout.setColumnStretch(6, 2.9)  # Carbon Sources
        filetrsPanel_layout.setColumnStretch(7, 2.3)  # Carbon Sources Groups

        # buttons panel
        filter_button = QPushButton("Filter")    
        filter_button.setFixedWidth(150)
        filter_button.clicked.connect(self.FilterButtonPushed) 
        save_button = QPushButton("Save to .csv")        
        save_button.setFixedWidth(150)
        save_button.clicked.connect(self.SaveButtonPushed)       

        buttonsPanel_layout.addWidget(filter_button)
        buttonsPanel_layout.addWidget(save_button)

        # main layout
        self.main_layout.addLayout(filetrsPanel_layout)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addLayout(buttonsPanel_layout)

        self.setLayout(self.main_layout)

        # FUNCTIONS
    def FilterButtonPushed(self):

        # clear previous filter data
        self.saved_data = []
        for i in reversed(range(self.displayPanel_layout.count())):
            self.displayPanel_layout.itemAt(i).widget().deleteLater()
       
        filtered_data = []
        for items in self.list_widget[:6]:
            selected_items = [item.text() for item in items.selectedItems()]
            filtered_data.append(selected_items)

        # default if no values
        filtered_data = [data if data else ['default'] for data in filtered_data]
        parameter_combinations = list(product(*filtered_data))

        # results 
        results = []

        for combination in parameter_combinations:
            criteria = {
                "bacteria": combination[0],
                "stressor": combination[1],
                "concentration": combination[2],
                "time": combination[3],
                "blank": combination[4],
                "repetition": combination[5]
            }


            # dynamic filtration based on criteria
            matching_records = None

            if criteria["blank"] != "default":
                blank_value = criteria["blank"] == "Yes"
                blank_records = set(self.records_dicts["blank"].get(blank_value, []))
                if matching_records is None:
                    matching_records = blank_records


            for key, value in criteria.items():
                if key == "blank":
                    continue


                if value == "default":
                    candidates = set(
                        record for records in self.records_dicts[key].values() for record in records
                        )
                else:
                    candidates = set(self.records_dicts[key].get(value, []))

                # initialization and narrowing down the records
                if matching_records is None:
                    matching_records = candidates
                else:
                    matching_records.intersection_update(candidates)

            
            if matching_records:
                results.extend(matching_records)

            results = list(set(results))


        # chcecking  if carbon source (groups) filters are choosen
        selected_carbon_sources = [item.text() for item in self.list_widget[6].selectedItems()]
        selected_carbon_groups = [item.text() for item in self.list_widget[7].selectedItems()]

        if selected_carbon_sources and selected_carbon_groups:
            QMessageBox.warning(self, "ERROR", "You can filter by carbon sources OR carbon sources groups.")
            return
                

    # Displaying filtered data

        for record in results:
            # no carbon source -> display full matrix
            if not selected_carbon_sources and not selected_carbon_groups:
                matrix = getattr(record, "ecoplate", [[0] * 4 for _ in range(8)])  
                record_widget = RecordWidget(record, matrix, 0) 
                self.displayPanel_layout.addWidget(record_widget)
                self.saved_data.append((record, matrix))        # for csv saving

            # carbon sources
            elif selected_carbon_sources and not selected_carbon_groups:
                coords = []
                
                for selected_source in selected_carbon_sources:
                    for row_idx, row in enumerate(self.carbon_sources):
                        if selected_source in row:
                            col_idx = row.index(selected_source)  # row id
                            coords.append((selected_source, row_idx, col_idx))  # adding coords (row, column)
                
                
                matrix = []
                for (selected_source, row_idx, col_idx) in coords:
                    value = record.ecoplate[row_idx][col_idx]  # taking value from ecoplate matrix
                    matrix.append([selected_source, value])


                record_widget = RecordWidget(record, matrix, 1) 
                self.displayPanel_layout.addWidget(record_widget)
                self.saved_data.append((record, matrix))        # for csv saving
        
            elif selected_carbon_groups and not selected_carbon_sources:
                coords = []

                for group in selected_carbon_groups:
                    if group in self.carbon_sources_groups:
                        group_sources = self.carbon_sources_groups[group]
                        for source in group_sources:
                            for row_idx, row in enumerate(self.carbon_sources):
                                if source in row:
                                    col_idx = row.index(source)
                                    coords.append((group, source, row_idx, col_idx))

                # Retrieve values from the ecoplate matrix
                matrix = []
                for (group, source, row_idx, col_idx) in coords:
                    value = record.ecoplate[row_idx][col_idx]  # Get value from the ecoplate matrix
                    matrix.append([group, source, value])

                # Create RecordWidget with the filtered data
                record_widget = RecordWidget(record, matrix, 2)
                self.displayPanel_layout.addWidget(record_widget)
                self.saved_data.append((record, matrix))        # for csv saving


    def SaveButtonPushed(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Filtered Data",
            os.getcwd(),
            "CSV Files (*.csv);;All Files (*)",
            options=options
        )

        if not file_path:
            return

        if not file_path.endswith(".csv"):
            file_path += ".csv"

        try:
            # Create and save CSV file from saved_data
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                writer.writerow(["Bacteria", "Stressor", "Concentration", "Time", "Blank", "Repetition"])

                # save the data
                for record, matrix in self.saved_data:
                    writer.writerow([
                        record.bacteria,
                        record.stressor,
                        record.concentration,
                        record.time,
                        record.blank,
                        record.repetition
                    ])
                    for row in matrix:
                        writer.writerow(row)  
                        
            # Clear saved_data after successful export
            self.saved_data = []

            # Show success message
            QMessageBox.information(self, "Success", f"Data saved successfully to {file_path}")

        except Exception as e:
            # Handle any errors during saving
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")


                


        
