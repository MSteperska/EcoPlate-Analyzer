# window with statistical tests

from PySide6.QtWidgets import (
    QMessageBox, 
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QListWidget, 
    QScrollArea, QFileDialog,
    QTableWidget, QTableWidgetItem)

from itertools import product

import csv
import math
import app_state
from RecordWidget import RecordWidget

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm


class TestsWindow(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setWindowTitle("EcoPlate Analyzer - Tests")
        self.appState = app_state.AppState.get_instance()
        self.result_type = "AWCD"  # Default result type for graphs

        self.saved_data = []        # container for all filtered data -> for .csv saving
        
        # saving sets for comboboxes options
        self.bacteria_set = self.appState.bacteria_set
        self.stressor_set = self.appState.stressor_set
        self.concentration_set = self.appState.concentration_set
        self.time_set = self.appState.time_set
        self.repetition_set = self.appState.repetition_set
        self.filename = self.appState.filename_set
        self.carbon_sources = self.appState.carbon_source_list
        self.carbon_sources_groups = self.appState.carbon_source_groups

        self.records_dicts = self.appState.Records_dict  
        self.all_records = self.appState.all_records     


        # layouts
        self.main_layout = QVBoxLayout()
        filetrsPanel_layout = QGridLayout()     # top
        viewAndTestsButtonsPanel_layout = QHBoxLayout()     # middle
        buttonsPanel_layout = QHBoxLayout()     # bottom
        self.displayPanel_layout = QVBoxLayout()    # view and tests
        testsButtonsPanel_layout = QVBoxLayout()    # view and tests

        # buttons tests panel
        AWCD_button = QPushButton("AWCD")
        AWCD_button.clicked.connect(self.CalculateAWCD)     
        AWCD_button.clicked.connect(lambda: self.SetResultType("AWCD")) 
        AWCD_button.setFixedWidth(150)

        SAWCD_button = QPushButton("SAWCD")
        SAWCD_button.clicked.connect(self.CalculateSAWCD)   
        SAWCD_button.setFixedWidth(150)
        SAWCD_button.clicked.connect(lambda: self.SetResultType("SAWCD")) 

        ShannonIndex_button = QPushButton("Shannon index")
        ShannonIndex_button.clicked.connect(self.CalculateShannonIndex) 
        ShannonIndex_button.setFixedWidth(150)
        ShannonIndex_button.clicked.connect(lambda: self.SetResultType("Shannon Index"))

        ShannonEvenness_button = QPushButton("Shannon evenness")
        ShannonEvenness_button.clicked.connect(self.CalculateShannonEvenness)   
        ShannonEvenness_button.setFixedWidth(150)
        ShannonEvenness_button.clicked.connect(lambda: self.SetResultType("Shannon Evenness"))

        testsButtonsPanel_layout.addWidget(AWCD_button)
        testsButtonsPanel_layout.addWidget(SAWCD_button)
        testsButtonsPanel_layout.addWidget(ShannonIndex_button)
        testsButtonsPanel_layout.addWidget(ShannonEvenness_button)

        # display panel
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(275)

        scroll_content_widget = QWidget()
        scroll_content_widget.setFixedWidth(850)
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

        # buttons panel
        filter_button = QPushButton("Filter")    
        filter_button.setFixedWidth(150)
        filter_button.clicked.connect(self.FilterButtonPushed) 

        save_button = QPushButton("Save results to .csv")      
        save_button.setFixedWidth(150)
        save_button.clicked.connect(self.SaveResultsToCSV)

        save_graph_button = QPushButton("Save the graph to .png")
        save_graph_button.setFixedWidth(150)
        save_graph_button.clicked.connect(self.SaveGraph)

        buttonsPanel_layout.addWidget(filter_button)
        buttonsPanel_layout.addWidget(save_graph_button)
        buttonsPanel_layout.addWidget(save_button)

        # view and tests buttons layout
        viewAndTestsButtonsPanel_layout.addLayout(testsButtonsPanel_layout)
        viewAndTestsButtonsPanel_layout.addWidget(self.scroll_area)

        # main layout
        self.main_layout.addLayout(filetrsPanel_layout)
        self.main_layout.addLayout(viewAndTestsButtonsPanel_layout)
        self.main_layout.addLayout(buttonsPanel_layout)

        self.setLayout(self.main_layout)


    # FUNCTIONS

    def SetResultType(self, result_type):
        """
        Update the result type and call the SaveGraph function.
        """
        self.result_type = result_type


    def FilterButtonPushed(self):
        
        self.saved_data = []
        filtered_data = []

        # Collect selected filters from the list widgets
        for items in self.list_widget[:6]:
            selected_items = [item.text() for item in items.selectedItems()]
            filtered_data.append(selected_items)


        # Use default values if no filters are selected
        filtered_data = [data if data else ['default'] for data in filtered_data]

        parameter_combinations = list(product(*filtered_data))

        # Store results of filtering
        results = []

        for combination in parameter_combinations:
            criteria = {
                "bacteria": combination[0],
                "stressor": combination[1],
                "concentration": combination[2],
                "time": combination[3],
                "blank": combination[4],
                "repetition": combination[5],
            }
            
            
            matching_records = None
            for key, value in criteria.items():
                if value == "default":  # Include all records for this criterion
                    candidates = set()
                    for records in self.records_dicts[key].values():
                        candidates.update(records)
                else:
                    candidates = set(self.records_dicts[key].get(value, []))
                
        
                if not candidates:  # Skip empty candidate sets to avoid premature filtering
                    continue

                if matching_records is None:
                    matching_records = candidates
                else:
                    matching_records.intersection_update(candidates)
                
                if not matching_records:  # If intersection is empty, break early
                    break

            # Only add non-empty results
            if matching_records:
                results.extend(matching_records)


        # After filtering, warn if no results were found
        if not results:
            QMessageBox.warning(self, "No Results", "No records match the selected filters.")

        # Clear previous display panel
        for i in reversed(range(self.displayPanel_layout.count())):
            self.displayPanel_layout.itemAt(i).widget().deleteLater()

        selected_carbon_sources = [item.text() for item in self.list_widget[6].selectedItems()]
        selected_carbon_groups = [item.text() for item in self.list_widget[7].selectedItems()]

        # Display and save filtered data based on the filters
        for record in results:
            if not selected_carbon_sources and not selected_carbon_groups:
                matrix = getattr(record, "ecoplate", [[0] * 4 for _ in range(8)])
                record_widget = RecordWidget(record, matrix, 0)
                self.displayPanel_layout.addWidget(record_widget)
                self.saved_data.append((record, matrix))

            elif selected_carbon_sources and not selected_carbon_groups:
                coords = []
                for selected_source in selected_carbon_sources:
                    for row_idx, row in enumerate(self.carbon_sources):
                        if selected_source in row:
                            col_idx = row.index(selected_source)
                            coords.append((selected_source, row_idx, col_idx))

                matrix = []
                for (selected_source, row_idx, col_idx) in coords:
                    value = record.ecoplate[row_idx][col_idx]
                    matrix.append([selected_source, value])

                record_widget = RecordWidget(record, matrix, 1)
                self.displayPanel_layout.addWidget(record_widget)
                self.saved_data.append((record, matrix))

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

                matrix = []
                for (group, source, row_idx, col_idx) in coords:
                    value = record.ecoplate[row_idx][col_idx]
                    matrix.append([group, source, value])

                record_widget = RecordWidget(record, matrix, 2)
                self.displayPanel_layout.addWidget(record_widget)
                self.saved_data.append((record, matrix))

            elif selected_carbon_sources and selected_carbon_groups:
                QMessageBox.warning(self, "ERROR", "You can filter by carbon sources OR carbon sources groups.")


    def ShowTestResults(self, results, result_type):
        """
        A function for showcasing various test results such as AWCD, SAWCD, Shannon Index, and Shannon Evenness.
        
        :param results: The results to be displayed (list of tuples, each containing a record and a value).
        :param result_type: A string specifying the type of result (e.g., 'AWCD', 'SAWCD', 'Shannon Index', etc.).
        """

        # Clear the previous display panel
        for i in reversed(range(self.displayPanel_layout.count())):
            self.displayPanel_layout.itemAt(i).widget().deleteLater()

        # Create a table widget
        table = QTableWidget()
        
        if result_type == 'AWCD':
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Bacteria", "Stressor", "Concentration", "Time", "Repetition", "AWCD"])
        elif result_type == 'SAWCD':
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["Bacteria", "Stressor", "Concentration", "Time", "Repetition", "Category", "SAWCD"])
        elif result_type == 'Shannon Index':
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Bacteria", "Stressor", "Concentration", "Time", "Repetition", "Shannon Index"])
        elif result_type == 'Shannon Evenness':
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Bacteria", "Stressor", "Concentration", "Time", "Repetition", "Shannon Evenness"])
        else:
            raise ValueError(f"Unknown result type: {result_type}")

        # Set row count based on the number of results
        table.setRowCount(len(results))

        # Populate the table with the results
        for row_idx, (record, value) in enumerate(results):
            table.setItem(row_idx, 0, QTableWidgetItem(record.bacteria))
            table.setItem(row_idx, 1, QTableWidgetItem(record.stressor))
            table.setItem(row_idx, 2, QTableWidgetItem(record.concentration))
            table.setItem(row_idx, 3, QTableWidgetItem(record.time))
            table.setItem(row_idx, 4, QTableWidgetItem(record.repetition))

            if result_type == 'AWCD':
                table.setItem(row_idx, 5, QTableWidgetItem(f"{value:.3f}"))
            elif result_type == 'SAWCD':
                table.setItem(row_idx, 5, QTableWidgetItem(value[0]))  # Category
                table.setItem(row_idx, 6, QTableWidgetItem(f"{value[1]:.3f}"))  # SAWCD
            elif result_type == 'Shannon Index':
                table.setItem(row_idx, 5, QTableWidgetItem(f"{value:.3f}"))
            elif result_type == 'Shannon Evenness':
                table.setItem(row_idx, 5, QTableWidgetItem(f"{value:.3f}"))

        # Add the table to the display panel
        self.displayPanel_layout.addWidget(table)


    def SaveResultsToCSV(self):

        """
        Save the filtered or calculated results to a .csv file.
        The file includes the appropriate fields based on the filtering criteria.
        """
        if not self.saved_data:
            QMessageBox.warning(self, "No Data", "Please filter or calculate data before saving.")
            return

        # Prompt the user to select a save location
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Results to CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)

        if not file_path:
            return  # User canceled the save dialog

        # Determine if filtering by carbon sources or groups
        is_filtering_by_carbon_sources = bool([item.text() for item in self.list_widget[6].selectedItems()])
        is_filtering_by_carbon_groups = bool([item.text() for item in self.list_widget[7].selectedItems()])

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)

                # Construct the header based on filtering criteria
                if is_filtering_by_carbon_sources:
                    header = ["Bacteria", "Stressor", "Concentration", "Time", "Repetition", "Blank", "Carbon Source", "SAWCD"]
                elif is_filtering_by_carbon_groups:
                    header = ["Bacteria", "Stressor", "Concentration", "Time", "Repetition", "Blank", "Carbon Source Group", "SAWCD"]
                else:
                    header = ["Bacteria", "Stressor", "Concentration", "Time", "Repetition", "Blank", "AWCD", "Shannon Index", "Shannon Evenness"]
                
                writer.writerow(header)

                # Write data rows
                for record, matrix in self.saved_data:
                    common_data = [
                        record.bacteria,
                        record.stressor,
                        record.concentration,
                        record.time,
                        record.repetition,
                        record.blank,
                    ]

                    if is_filtering_by_carbon_sources:
                        sawcd_results = self.CalculateSAWCD()  # Get the SAWCD results
                        for group, sawcd in sawcd_results:
                            group_name = group 
                            sawcd_value = sawcd 
                            writer.writerow(common_data + [group_name, sawcd_value])
                    
                    elif is_filtering_by_carbon_groups:
                        sawcd_results = self.CalculateSAWCD()  # Get the SAWCD results
                        for record_result, (group, sawcd) in sawcd_results:
                            if record_result == record:
                                group_name = group  
                                sawcd_value = sawcd 
                                writer.writerow(common_data + [group_name, sawcd_value])
                    
                    else:
                        # Calculate and retrieve AWCD, Shannon Index, and Shannon Evenness values
                        awcd_results = self.CalculateAWCD()
                        shannon_index_results = self.CalculateShannonIndex()  # Get the Shannon Index
                        shannon_evenness_results = self.CalculateShannonEvenness()  # Get the Shannon Evenness

                        # match calculated values to the record
                        awcd = next((result[1] for result in awcd_results if result[0] == record), "N/A")
                        shannon_index = next((result[1] for result in shannon_index_results if result[0] == record), "N/A")
                        shannon_evenness = next((result[1] for result in shannon_evenness_results if result[0] == record), "N/A")

                        writer.writerow(common_data + [awcd, shannon_index, shannon_evenness])

            QMessageBox.information(self, "Success", f"Results successfully saved to {file_path}.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the file:\n{e}")


    def CalculateAWCD(self):
        """
        A function to calculate AWCD for the saved data and display the results.
        Returns a list of tuples with the original record and the AWCD value.
        """

        if not self.saved_data:
            QMessageBox.warning(self, "No Data", "Please filter the data first before calculating AWCD.")
            return []
        
        # If there are selected carbon sources or groups, don't proceed
        selected_carbon_sources = [item.text() for item in self.list_widget[6].selectedItems()]
        selected_carbon_groups = [item.text() for item in self.list_widget[7].selectedItems()]
        if selected_carbon_sources or selected_carbon_groups:
            QMessageBox.warning(self, "Invalid Selection", "Please do not select any carbon source or carbon source group when calculating AWCD.")
            return [] 

        awcd_results = []  # Store the AWCD results for each record

        for record, matrix in self.saved_data:
            awcd = 0
            total_wells = 0
            first_value_skipped = False  # To skip the first value (water well)

            for row in matrix:
                if isinstance(row, list): 
                    for value in row:
                        try:
                            value = float(value)

                            # Skip the first value (water well)
                            if not first_value_skipped:
                                first_value_skipped = True
                                continue

                            awcd += value
                            total_wells += 1
                        except ValueError:
                            pass

            if total_wells > 0:
                awcd /= total_wells

            awcd_results.append((record, awcd))

        self.ShowTestResults(awcd_results, 'AWCD')

        return awcd_results


    def CalculateSAWCD(self):
        """
        A function to calculate SAWCD for the saved data and showcase the results.
        """
        if not self.saved_data:
            QMessageBox.warning(self, "No Data", "Please filter the data first before calculating SAWCD.")
            return []
        
        selected_carbon_sources = [item.text() for item in self.list_widget[6].selectedItems()]
        if selected_carbon_sources:
            QMessageBox.warning(self, "Invalid Selection", "Please do not select any carbon source when calculating SAWCD.")
            return []  

        # Get selected categories from the filters
        selected_carbon_groups = [item.text() for item in self.list_widget[7].selectedItems()]
        if not selected_carbon_groups:
            QMessageBox.warning(self, "No Category Selected", "Please select at least one substrate category.")
            return []
        

        sawcd_results = []
        for record, matrix in self.saved_data:
            # For each selected carbon group
            for group in selected_carbon_groups:
                sawcd = 0
                total_wells = 0

                # Calculate SAWCD for the current group
                if group in self.carbon_sources_groups:
                    group_sources = self.carbon_sources_groups[group]

                    for source in group_sources:
                        found = False
                        for matrix_row in matrix:
                            if len(matrix_row) >= 3 and matrix_row[1] == source:
                                try:
                                    value = float(matrix_row[2])
                                    if value < 0:
                                        value = 0  
                                    sawcd += value
                                    total_wells += 1
                                    found = True
                                    break
                                except (ValueError, IndexError):
                                    pass

                # Calculate the average for the selected category
                if total_wells > 0:
                    sawcd /= total_wells

                # Append the result as a tuple of the record and the calculated SAWCD
                sawcd_results.append((record, (group, sawcd)))

            self.ShowTestResults(sawcd_results, 'SAWCD')

        return sawcd_results  # Return the results


    def CalculateShannonIndex(self):
        """
        A function to calculate Shannon Index for the saved data and showcase the results.
        Returns a list of tuples with the original record and the Shannon Index value.
        """
        # Check if the saved data is populated
        if not self.saved_data:
            QMessageBox.warning(self, "No Data", "Please filter the data first before calculating Shannon Index.")
            return []  
        
        selected_carbon_sources = [item.text() for item in self.list_widget[6].selectedItems()]
        selected_carbon_groups = [item.text() for item in self.list_widget[7].selectedItems()]
        if selected_carbon_sources or selected_carbon_groups:
            QMessageBox.warning(self, "Invalid Selection", "Please do not select any carbon source or carbon source group when calculating Shannon Index.")
            return [] 

        shannon_index_results = []  # List to store the results

        for record, matrix in self.saved_data:
            # Check if matrix is valid (a list of lists) and contains numeric values
            if not isinstance(matrix, list):
                QMessageBox.warning(self, "Invalid Data", f"Invalid data format for record {record}. Skipping this record.")
                continue
            
            total_development = 0.0
            valid_values = []  # List to store valid values (positive values from the matrix)
            first_value_skipped = False  # Flag to skip the first value (water)


            for row in matrix:
                if isinstance(row, list):  
                    for value in row:
                        try:
                            value = float(value)  

                            if not first_value_skipped:
                                first_value_skipped = True
                                continue  # Skip the first value (water)
                            
                            if value > 0: 
                                valid_values.append(value)
                                total_development += value
                        except ValueError:
                            pass  

            # Ensure that there are valid values to calculate Shannon Index
            if total_development > 0:
                proportions = [val / total_development for val in valid_values]
                shannon_index = -sum(p * math.log(p) for p in proportions if p > 0)
            else:
                shannon_index = 0.0  # If no valid values, set Shannon Index to 0

            shannon_index_results.append((record, shannon_index))

        if shannon_index_results:
            self.ShowTestResults(shannon_index_results, 'Shannon Index')

        return shannon_index_results



    def CalculateShannonEvenness(self):
        """
        A function to calculate Shannon Evenness for the saved data and showcase the results.
        Returns a list of tuples with the original record and the Shannon Evenness value.
        """
        # Check if the saved data is populated
        if not self.saved_data:
            QMessageBox.warning(self, "No Data", "Please filter the data first before calculating Shannon Evenness.")
            return [] 
        
        selected_carbon_sources = [item.text() for item in self.list_widget[6].selectedItems()]
        selected_carbon_groups = [item.text() for item in self.list_widget[7].selectedItems()]
        if selected_carbon_sources or selected_carbon_groups:
            QMessageBox.warning(self, "Invalid Selection", "Please do not select any carbon source or carbon source group when calculating Shannon Evenness.")
            return []

        shannon_evenness_results = []  # List to store the results

        for record, matrix in self.saved_data:
            # Check if matrix is valid (a list of lists) and contains numeric values
            if not isinstance(matrix, list):
                QMessageBox.warning(self, "Invalid Data", f"Invalid data format for record {record}. Skipping this record.")
                continue

            total_development = 0.0
            valid_values = []  # List to store valid values (positive values from the matrix)
            first_value_skipped = False  # Flag to skip the first value (water))


            for row in matrix:
                if isinstance(row, list):  
                    for value in row:
                        try:
                            value = float(value)  

                            if not first_value_skipped:
                                first_value_skipped = True
                                continue  # Skip the first value (water)
                            
                            if value > 0:  
                                valid_values.append(value)
                                total_development += value
                        except ValueError:
                            pass  

            # Ensure that there are valid values to calculate Shannon Evenness
            if total_development > 0:
                proportions = [val / total_development for val in valid_values]
                shannon_index = -sum(p * math.log(p) for p in proportions if p > 0)
            else:
                shannon_index = 0.0  # If no valid values, set Shannon Index to 0

            # Calculate the Shannon Evenness
            S = len(valid_values)
            if S > 0:
                shannon_evenness = shannon_index / math.log(S)
            else:
                shannon_evenness = 0.0  # No evenness if no valid values are present

            shannon_evenness_results.append((record, shannon_evenness))

        if shannon_evenness_results:
            self.ShowTestResults(shannon_evenness_results, 'Shannon Evenness')

        return shannon_evenness_results


    def SaveGraph(self):
        """
        A function to generate and save a bar graph for the selected test results (AWCD, Shannon Index, Shannon Evenness, or SAWCD),
        including distinguishing blank samples as a separate group.
        """

        # Check for saved data
        if not self.saved_data:
            QMessageBox.warning(self, "No Data", "Please filter the data first before generating the graph.")
            return

        # Determine the type of result to plot
        result_type = self.result_type

        # Extract the selected stressor
        selected_stressors = [item.text() for item in self.list_widget[1].selectedItems()]
        if not selected_stressors:
            QMessageBox.warning(self, "No Stressor Selected", "Please select a stressor before saving the graph.")
            return
        stressor = ", ".join(selected_stressors)

        if result_type == "SAWCD":

            selected_stressors = [item.text() for item in self.list_widget[1].selectedItems()]
            if not selected_stressors:
                QMessageBox.warning(self, "No Stressor Selected", "Please select a stressor before saving the graph.")
                return
            stressor = ", ".join(selected_stressors)

            # Extract selected carbon groups
            selected_carbon_groups = [item.text() for item in self.list_widget[7].selectedItems()]
            if not selected_carbon_groups:
                QMessageBox.warning(self, "No Category Selected", "Please select at least one substrate category.")
                return

            # Calculate SAWCD results
            sawcd_results = self.CalculateSAWCD()
            if not sawcd_results:
                return

            # Extract unique concentrations, times, and groups

            bacterias = set(record.bacteria for record, _ in sawcd_results)
            bacteria_name = ", ".join(bacterias) if len(bacterias) > 1 else next(iter(bacterias), "Unknown")
            concentrations = sorted(set(record.concentration for record, _ in sawcd_results))
            times = sorted(set(record.time for record, _ in sawcd_results))
            groups = selected_carbon_groups

            # Initialize grouped data structure
            grouped_data = {
                (conc, time): {group: 0 for group in groups}
                for conc in concentrations for time in times
            }

            # Populate grouped data with SAWCD values
            for record, (group, sawcd) in sawcd_results:
                if group in grouped_data[(record.concentration, record.time)]:
                    grouped_data[(record.concentration, record.time)][group] += sawcd


            # Normalize values to percentages
            normalized_data = {
                key: {
                    group: (value / sum(data.values()) * 100 if sum(data.values()) > 0 else 0)
                    for group, value in data.items()
                }
                for key, data in grouped_data.items()
            }


            # Prepare the plot
            fig, ax = plt.subplots(figsize=(12, 8))
            bar_width = 0.8  # Single bar width for stacked bars
            x_positions = np.arange(len(normalized_data))  # X positions for each concentration-time pair

            # Assign colors to groups
            color_map = plt.get_cmap("Set2")
            group_colors = {group: color_map(idx / len(groups)) for idx, group in enumerate(groups)}

            # Plot stacked bars
            bottom_values = np.zeros(len(normalized_data))  # Initialize bottom values for stacking
            sorted_keys = sorted(normalized_data.keys())   # Ensure consistent key order
            for group in groups:
                values = [normalized_data[key][group] for key in sorted_keys]
                ax.bar(
                    x_positions,
                    values,
                    bar_width,
                    bottom=bottom_values,
                    color=group_colors[group],
                    label=group
                )
                bottom_values += values  # Accumulate for stacking

            # Customize x-axis labels
            labels = [f"{time} h\n{conc} ppm" for conc, time in sorted_keys]
            ax.set_xticks(x_positions)
            ax.set_xticklabels(labels, rotation=45, ha="right")

            # Add labels, title, and legend
            ax.set_xlabel(f"{stressor} concentration [ppm]")
            ax.set_ylabel("Utilization rate of substrates [%]")
            ax.set_title(f'{result_type} for {bacteria_name} consortium')
            ax.legend(title="Carbon Source Groups", bbox_to_anchor=(1.05, 1), loc='upper left')

            # Save the graph
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "PNG files (*.png);;PDF files (*.pdf)")
            if file_name:
                plt.tight_layout()
                plt.savefig(file_name, format="png" if file_name.endswith(".png") else "pdf", bbox_inches="tight")
                QMessageBox.information(self, "Graph Saved", f"Graph has been saved to {file_name}.")

            plt.close(fig)

            
        else:
            # Handle AWCD, Shannon Index, or Shannon Evenness using the swapped implementation
            if result_type == "AWCD":
                calculated_results = self.CalculateAWCD()
            elif result_type == "Shannon Index":
                calculated_results = self.CalculateShannonIndex()
            elif result_type == "Shannon Evenness":
                calculated_results = self.CalculateShannonEvenness()
            else:
                QMessageBox.warning(self, "Invalid Result Type", "Unsupported result type selected.")
                return

            # Prepare data for plotting
            results = []
            for (record, matrix), (_, result_value) in zip(self.saved_data, calculated_results):
                is_blank = record.blank == "Yes"  # Check if the record is marked as "blank"
                results.append({
                    'bacteria': record.bacteria,
                    'stressor': record.stressor,
                    'concentration': "Blank" if is_blank else record.concentration,  # Replace concentration with "Blank" for blanks
                    'time': record.time,
                    'value': result_value
                })

            # Organize data
            concentrations = sorted(set(result['concentration'] for result in results if result['concentration'] != "Blank"))
            if any(result['concentration'] == "Blank" for result in results):
                concentrations = ["Blank"] + concentrations  # Ensure "Blank" is the first in the order

            times = sorted(set(result['time'] for result in results))
            bacteria_set = set(result['bacteria'] for result in results)
            bacteria_name = ", ".join(bacteria_set) if len(bacteria_set) > 1 else next(iter(bacteria_set), "Unknown")

            # Dictionary to store values grouped by concentration and time
            grouped_data = {conc: {time: [] for time in times} for conc in concentrations}
            for result in results:
                conc = result['concentration']  # "Blank" or the actual concentration
                if result['value'] is not None:
                    grouped_data[conc][result['time']].append(result['value'])

            # Prepare the plot
            fig, ax = plt.subplots(figsize=(12, 8))
            bar_width = 0.25
            x_positions = np.arange(len(concentrations))

            colormap = cm.get_cmap("Set2", len(times))  # Set2 with discrete colors
            time_colors = [colormap(i) for i in range(len(times))]

            # Plot data
            for t_idx, time in enumerate(times):
                values = [
                    np.mean(grouped_data[conc][time]) if grouped_data[conc][time] else 0
                    for conc in concentrations
                ]
                ax.bar(
                    x_positions + t_idx * bar_width,
                    values,
                    bar_width,
                    label=f"{time} hours",
                    color=time_colors[t_idx]  # Use Set2 colors
                )

            # Add labels and formatting
            ax.set_xlabel(f'{stressor} concentration [ppm]')
            ax.set_ylabel(result_type)
            ax.set_title(f'{result_type} for {bacteria_name} consortium')
            ax.set_xticks(x_positions + bar_width * (len(times) - 1) / 2)
            ax.set_xticklabels([str(conc) if conc != "Blank" else "Blank" for conc in concentrations])  # Use "Blank" label
            ax.legend(title="Time", bbox_to_anchor=(1.05, 1), loc='upper left')

            # Save the graph to a file
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "PNG files (*.png);;PDF files (*.pdf)")
            if file_name:
                plt.tight_layout()
                plt.savefig(file_name, format="png" if file_name.endswith(".png") else "pdf", bbox_inches="tight")
                QMessageBox.information(self, "Graph Saved", f"Graph has been saved to {file_name}.")

            plt.close(fig)
