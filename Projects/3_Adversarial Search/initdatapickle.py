import pickle
import pandas as pd

df = pd.DataFrame(columns=['board', 'plycount', 'locs', 'action', 'utility', 'visit', 'nround', 'score'])
with open('data.pickle', 'wb') as pfile:
    pickle.dump(df, pfile)