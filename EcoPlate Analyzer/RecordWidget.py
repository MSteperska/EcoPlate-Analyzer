# Record widget class for filtered data display

from PySide6.QtWidgets import (QWidget, QGridLayout, QLabel, 
                               QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt


class RecordWidget (QWidget):
    def __init__(self, record, matrix, mode):
        super().__init__()

        grid_layout = QGridLayout()

        keys = ["bacteria", "stressor", "concentration", "time", "blank", "repetition"]
        for row, key in enumerate(keys):

            key_label = QLabel(f"{key}:")
            grid_layout.addWidget(key_label, row, 0)
    
            value = getattr(record, key, "N/A")
            value_label = QLabel(str(value))
            grid_layout.addWidget(value_label, row, 1)

        # table for ecoplate
        table = QTableWidget()
        table.setRowCount(len(matrix)) 
        table.setColumnCount(len(matrix[0]))

        # no carbon source
        if mode == 0:
            table.setHorizontalHeaderLabels(["1", "2", "3", "4"])
            table.setVerticalHeaderLabels(["A", "B", "C", "D", "E", "F", "G", "H"])
            for i in range(4):
                table.setColumnWidth(i, 50)

            # filling matrix with ecoplate info
            for row in range(len(matrix)):
                for col in range(len(matrix[row])):
                    item = QTableWidgetItem(str(matrix[row][col]))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row, col, item)

        # carbon sources
        elif mode == 1:
            carbon_sources = [row[0] for row in matrix]  # carbon source labels 
            table.setVerticalHeaderLabels(carbon_sources)
            table.setColumnCount(1)
            table.setHorizontalHeaderLabels(["Value"])
            table.setColumnWidth(0, 50)

            # filling matrix with ecoplate info
            for row in range(len(matrix)):
                item = QTableWidgetItem(str(matrix[row][1]))  # matrix[row][1] is the value from the second column
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, item)  # Set in the first column (column 0)

        # carbon sources groups
        elif mode == 2:
            groups = [row[0]for row in matrix]
            table.setVerticalHeaderLabels(groups) 
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Carbon source", "Value"])
            table.setColumnWidth(0, 150)
            table.setColumnWidth(1, 50)

            # filling matrix with ecoplate info
            for row in range(len(matrix)):
                source = QTableWidgetItem(str(matrix[row][1]))
                item = QTableWidgetItem(str(matrix[row][2]))  # matrix[row][1] is the value from the second column
                source.setFlags(source.flags() & ~Qt.ItemIsEditable)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, source) 
                table.setItem(row, 1, item)



        grid_layout.addWidget(table, 0, 2, len(keys), 1)

        self.setLayout(grid_layout)
        self.setFixedSize(600, 300)
