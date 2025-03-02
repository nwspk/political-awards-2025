#%%
## Run this to set up
import pandas as pd
from pathlib import Path

#%%
## Just choose one of the below patterns, according to what you want to see
which_file = 'grantmaking_*.csv'
#%%
which_file = 'enriched_websites_*.csv'
#%%
which_file = 'projects*.csv'

#%%
## Now run this to load the data
data_dir = '../data'
most_recent = sorted(Path(data_dir).glob(which_file))[-1]
df = pd.read_csv(Path(data_dir) / most_recent.name)

#%%
## Explore the data however you choose
df.head()

# %%
