# Record class
'''Class for ecoplate experiment results with added info (1/3 of ecoplate)'''

class EcoplateExperimentRecord:

    def __init__(self, bacteria, stressor, concentration, time, blank, repetition, ecoplate, file_name):
        self.bacteria = bacteria
        self.stressor = stressor
        self.concentration = concentration
        self.time = time
        self.blank = blank
        self.repetition = repetition
        self.ecoplate = ecoplate
        self.file_name = file_name


