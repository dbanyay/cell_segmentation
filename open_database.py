import numpy as np
from Bio.Affy import CelFile
from pathlib import Path
import GEOparse
import pandas as pd
from matplotlib import pyplot as plt

path = Path("C:/Users/Daniel/Desktop/Andi project/database/Soft/GSE64392_family.soft")
num_top_n = 50

gse = GEOparse.get_GEO(filepath=str(path))

cntr = 1
for gsm_name, gsm in gse.gsms.items():
    print(f"Analysing dataset {cntr}/{len(gse.gsms)}")

    temp_df = pd.DataFrame(data=gsm.table["VALUE"].values.transpose(), index=gsm.table["ID_REF"], columns=[gsm_name])

    if cntr == 1:
        joined_df = temp_df.copy()

    else:
        joined_df = joined_df.join(temp_df)

    cntr += 1

sorted_means = joined_df.mean(axis=1).sort_values(ascending=False)[:num_top_n]

gpl_table = gse.gpls[list(gse.gpls.keys())[0]].table

gene_info = []
gb_acc_list = []
for key in list(sorted_means.keys()):
    gene_info.append(gpl_table.loc[gpl_table['ID'] == str(key)])
    gb_acc = gpl_table.loc[gpl_table['ID'] == str(key)]['GB_ACC'].values[0]

    if type(gb_acc) is not str:
        gb_acc_list.append(f'ID: {str(key)}')
    else:
        gb_acc_list.append(f'GB_ACC: {gb_acc}')

print(f'top {num_top_n} genes with highest average:')
print(sorted_means.head(num_top_n))

plt.bar(range(num_top_n), sorted_means.values[:num_top_n])
plt.xticks(range(num_top_n), gb_acc_list, rotation='vertical')
plt.title(f'Top {num_top_n} highest average of {len(gse.gsms)} samples')
plt.ylabel('Average VALUE')
plt.xlabel('ID_REF')
plt.tight_layout()

plt.show()
