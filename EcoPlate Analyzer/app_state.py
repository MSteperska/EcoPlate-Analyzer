#   app state

'''Class that manages the application state, 
    stores constant data sets
    and nested dictionary for ecoplateExperiment records'''

class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

         # data sets for input info
        self.bacteria_set = set()
        self.stressor_set = set()
        self.concentration_set = set()
        self.time_set = set()
        self.repetition_set = set()
        self.filename_set = set()

        # carbon sources matrix 
        self.carbon_source_list = [["" for _ in range(4)] for _ in range(8)]
        carbon_sources = [
            ["Water", "Betha-Methyl-D-Glucoside", "D-Galactonic Acid gamma-Lactone", "L-Arginine"],
            ["Pyruvic Acid Methyl Ester", "D-Xylose", "D-Galacturonic Acid", "L-Asparagine"],
            ["Tween 40", "i-Erythritol", "2-HydroxyBenzoic Acid", "L-Phenylalanine"],
            ["Tween 80", "D-Mannitol", "4-HydroxyBenzoic Acid", "L-Serine"],
            ["Alpha-Cyclodextrin",  "N-Acetyl-D-Glucosamine", "Gamma-Amino Butyric Acid", "L-Threonine"],
            ["Glycogen", "D-Glucosaminic Acid", "Itaconic Acid", "Betha-HydroxyGlycyl-L-Glutamic Acid"],
            ["D-Cellobiose", "Glucose-1-Phosphate", "Alpha-KetoButyric Acid", "Phenylethylamine"],
            ["Alpha-D-Lactose", "D,L-alpha-Glycerol Phosphate", "D-Malic Acid", "Putrescine"]
        ]

        for i in range(8):
            for j in range(4):
                self.carbon_source_list[i][j] = carbon_sources[i][j]

        # carbon sources groups
        self.carbon_source_groups = {
            "polymers": ["Tween 40", "Tween 80", "Alpha-Cyclodextrin", "Glycogen"],
            "carbohydrates" : ["D-Cellobiose", "Alpha-D-Lactose", "Betha-Methyl-D-Glucoside", 
                            "D-Xylose", "i-Erythritol", "D-Mannitol", "N-Acetyl-D-Glucosamine",
                            "Glucose-1-Phosphate", "D,L-alpha-Glycerol Phosphate", "D-Galactonic Acid gamma-Lactone"],
            "carboxylic acids": ["D-Galacturonic Acid", "Pyruvic Acid Methyl Ester","D-Glucosaminic Acid",
                            "Gamma-Amino Butyric Acid", "Itaconic Acid", "Alpha-KetoButyric Acid", "D-Malic Acid"],
            "aminoacids": ["L-Asparagine", "L-Arginine", "L-Phenylalanine", "L-Serine", "L-Threonine", "Betha-HydroxyGlycyl-L-Glutamic Acid"],
            "amines": ["Phenylethylamine" ,"Putrescine"],
            "phenolic compounds": ["2-HydroxyBenzoic Acid", "4-HydroxyBenzoic Acid"]
        }

        #   nested dictionary for EcoplateExperimentRecords
        self.Records_dict = {
            'bacteria': {},
            'stressor': {}, 
            'concentration': {},
            'time': {},
            'blank': {},
            'repetition': {},
            'filename': {}
        }
        
        #   variable for EcoplateExperimentRecords all records
        self.all_records = []


    @classmethod
    def get_instance(cls):
        """Class method that returns the only instance of AppState"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

