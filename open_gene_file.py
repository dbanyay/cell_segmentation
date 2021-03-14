import numpy as np
from pathlib import Path
import GEOparse
import pandas as pd
from matplotlib import pyplot as plt

path = Path("C:/Users/Daniel/Desktop/Andi project/database/Soft/GPL16686_family.soft.gz")

gse = GEOparse.get_GEO(filepath=str(path), partial=['GPL16686'])

gpl_table = gse.gpls[list(gse.gpls.keys())[0]].table

print('Finished!')