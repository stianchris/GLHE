#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import sys

import pandas as pd
import numpy as np


# In[ ]:


cwd = os.getcwd()
join = os.path.join
norm = os.path.normpath


# In[ ]:


import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


plt.style.use('seaborn-bright')
plt.rcParams['figure.figsize'] = [15, 9]
plt.rcParams['font.size'] = 12


# In[ ]:


sys.path.append(norm(join(cwd, '..', '..', '..', 'glhe')))


# In[ ]:


from standalone.plant_loop import PlantLoop
import glhe


# In[ ]:


d = glhe.utilities.functions.load_json('Neighbor_GHEs.json')

# d['ground-heat-exchanger'][0]['g-function-path'] = join(cwd, 'g.csv')
d['ground-heat-exchanger'][0]['simulation-mode'] = 'direct'

d['load-profile'] = [{}]
d['load-profile'][0]['load-profile-type'] = 'constant'
d['load-profile'][0]['name'] = 'constant load'
d['load-profile'][0]['value'] = 1500

d['flow-profile'][0]['value'] = 0.446

d.pop('swedish-heat-pump')
d['topology']['demand-side'][1] = {'comp-type': 'load-profile', 'name': 'constant load'}

d['simulation']['runtime'] = 3600 * 48
d['simulation']['time-step'] = 60

f_in = 'in_direct.json'
f_out = 'out_direct.csv'    

d['simulation']['output-csv-name'] = f_out
d['simulation']['output-path'] = cwd

glhe.utilities.functions.write_json(f_in, d)

PlantLoop(f_in).simulate()

alpha = d['soil']['conductivity'] / (d['soil']['density'] * d['soil']['specific-heat'])
h = d['borehole-definitions'][0]['length']
ts = h ** 2 / (9 * alpha)

df = pd.read_csv('out_direct.csv', index_col=0, parse_dates=True)

df['lntts'] = np.log(df['Elapsed Time [s]'] / ts)

df['Rb'] = df['SingleUTubeBHGrouted:BH 1:BH Resist. [m-K/W]']

df['gb'] = (df['GroundHeatExchangerSTS:SELF-GHE:Outlet Temp. [C]'] - df['GroundHeatExchangerSTS:SELF-GHE:Borehole Wall Temp. [C]']) / (df['GroundHeatExchangerSTS:SELF-GHE:Heat Rate [W]'] * df['Rb'] / h)


# In[ ]:


df.columns


# In[ ]:


df['SingleUTubeBHGrouted:BH 1:BH Resist. [m-K/W]'].plot()


# In[ ]:


plt.plot(df['lntts'], df['gb'])


# In[ ]:


lntts = df['lntts'].values
gb = df['gb'].values


# In[ ]:


lntts, gb = glhe.utilities.functions.resample_g_functions(lntts, gb)


# In[ ]:


arr = np.array([lntts, gb])


# In[ ]:


glhe.utilities.functions.write_arrays_to_csv(join(cwd, 'gb_out.csv'), arr)


# In[ ]:




