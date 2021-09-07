#!/usr/bin/env python
# coding: utf-8
"""


"""

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


def run_sim(years_to_sim, num_cross=None, years_to_delay_cross=None, dist_cross=None, testing=False, printing=False):

    d = glhe.utilities.functions.load_json('Neighbor_GHEs.json')
    
    d['ground-heat-exchanger'][0]['g-function-path'] = join(cwd, 'g.csv')
    d['ground-heat-exchanger'][0]['g_b-function-path'] = join(cwd, 'g_b.csv')
    d['ground-heat-exchanger'][0]['g_b-flow-rates'] = [0.43, 0.46]

    if num_cross:
        d['ground-heat-exchanger'][0]['cross-loads'] = [{}]
        
        if dist_cross == 10:
            d['ground-heat-exchanger'][0]['cross-loads'][0]['g-function-path'] = join(cwd, 'g_cross_10m.csv')
        elif dist_cross == 15:
            d['ground-heat-exchanger'][0]['cross-loads'][0]['g-function-path'] = join(cwd, 'g_cross_15m.csv')
        elif dist_cross == 20:
            d['ground-heat-exchanger'][0]['cross-loads'][0]['g-function-path'] = join(cwd, 'g_cross_20m.csv')
        
        d['ground-heat-exchanger'][0]['cross-loads'][0]['load-data-path'] = join(cwd, 'Cross_Loads.csv')
        d['ground-heat-exchanger'][0]['cross-loads'][0]['start-time'] = 3600 * 24 * 365 * years_to_delay_cross
        d['ground-heat-exchanger'][0]['cross-loads'][0]['number-of-instances'] = num_cross
        d['ground-heat-exchanger'][0]['cross-loads'][0]['length'] = 150  # length of one borehole

    d['swedish-heat-pump'][0]['load-data-path'] = join(cwd, 'HP_Loads_ODT.csv')
    d['flow-profile'][0]['path'] = join(cwd, 'HP_Loads_ODT.csv')

    d['simulation']['runtime'] = 3600 * 24 * 365 * years_to_sim
    
    if testing:
        f_in = 'in.json'
        f_out = 'out.csv'    
    elif num_cross:
        f_in = 'in_{}-yr_{}-cross_{}-m_start-{}-yr.json'.format(years_to_sim, num_cross, dist_cross, years_to_delay_cross)
        f_out = 'out_{}-yr_{}-cross_{}-m_start-{}-yr.csv'.format(years_to_sim, num_cross, dist_cross, years_to_delay_cross)
    else:
        f_in = 'in_{}-yr_self.json'.format(years_to_sim)
        f_out = 'out_{}-yr_self.csv'.format(years_to_sim)
        
    d['simulation']['output-csv-name'] = f_out
    d['simulation']['output-path'] = cwd

    glhe.utilities.functions.write_json(f_in, d)
    
    PlantLoop(f_in).simulate(printing=printing)


# In[ ]:


run_sim(20, testing=False, printing=True)
# run_sim(20, testing=False)


# In[ ]:


run_sim(20, num_cross=1, years_to_delay_cross=0, dist_cross=10, printing=True)
# run_sim(20, num_cross=1, years_to_delay_cross=0, dist_cross=10)


# In[ ]:


run_sim(20, num_cross=1, years_to_delay_cross=0, dist_cross=15)


# In[ ]:


run_sim(20, num_cross=1, years_to_delay_cross=0, dist_cross=20)


# In[ ]:


def resample_data(df, freq):
    
    df_sums = df.copy(deep=True)
    df_means = df.copy(deep=True)
    
    df_sums = df_sums.resample(freq).sum()
    df_means = df_means.resample(freq).mean()
    
    for col in df_sums.columns:
        if '[W]' in col:
            # drop col from means
            df_means.drop(col, axis=1, inplace=True)
            
            # convert W to kWh. assuming a 1 hour timestep
            df_sums[col] = df_sums[col]  / 1000
            
            # rename
            new_name = col.replace('[W]', '[kWh]')
            df_sums.rename(columns={col: new_name}, inplace=True)
            
        else:
            # drop col from sums
            df_sums.drop(col, axis=1, inplace=True)
            
    df_temp = pd.concat([df_sums, df_means], axis=1, sort=True)
    return df_temp.reindex(sorted(df_temp.columns), axis=1)


# In[ ]:


# df_self = pd.read_csv('out_1-yr_self.csv', index_col=0, parse_dates=True)
df_self = pd.read_csv('out_20-yr_self.csv', index_col=0, parse_dates=True)
# df_cross = pd.read_csv('out_1-yr_1-cross_10-m_start-0-yr.csv', index_col=0, parse_dates=True)


# In[ ]:


# df_self = resample_data(df_self, 'M')
# df_cross = resample_data(df_cross, 'M')


# In[ ]:


print(df_self.columns)


# In[ ]:


fig = plt.figure()

ax = fig.add_subplot(111)

cols = [
    # 'GroundHeatExchangerLTS:SELF-GHE:BH Resist. [m-K/W]',
    # 'GroundHeatExchangerLTS:SELF-GHE:Heat Rate [W]',
    'GroundHeatExchangerLTS:SELF-GHE:Inlet Temp. [C]',
    'GroundHeatExchangerLTS:SELF-GHE:Outlet Temp. [C]',
    # 'SwedishHP:SVENSKA VARMMEPUMPE:COP [-]',
    'SwedishHP:SVENSKA VARMMEPUMPE:Outdoor Air Temp. [C]',
    # 'SwedishHP:SVENSKA VARMMEPUMPE:Load-side Heat Rate [W]',
    # 'PlantLoop:Demand Inlet Temp. [C]',
    # 'PlantLoop:Demand Outlet Temp. [C]',
    # 'PlantLoop:Supply Inlet Temp. [C]',
    # 'PlantLoop:Supply Outlet Temp. [C]',
    # 'ConstantFlow:CONSTANT FLOW:Flow Rate [kg/s]',
    # 'SwedishHP:SVENSKA VARMMEPUMPE:Outlet Temp. [C]',
    # 'SwedishHP:SVENSKA VARMMEPUMPE:Inlet Temp. [C]',
    # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Heat Rate [W]',
    # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:BH Heat Rate [W]',
    # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Inlet Temp. [C]',
    # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Outlet Temp. [C]',
    # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Inlet Temp. Leg 1 [C]',
    # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Inlet Temp. Leg 2 [C]',
    # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Outlet Temp. Leg 1 [C]',
    # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Outlet Temp. Leg 2 [C]',
    # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:2:Outlet Temp. [C]',
    ]

for col in cols: 
    ax.plot(df_self[col], label=col)
    # ax.plot(df_cross[col], label=col+"cross")


plt.legend()
plt.show()


# In[ ]:


df_march_self = df_self.loc[df_self.index.month==3]
# df_march_cross = df_cross.loc[df_cross.index.month==3]


# In[ ]:


fig = plt.figure()

ax = fig.add_subplot(111)

x = range(1, df_march_self.shape[0] + 1)

ax.bar(x, df_march_self['SwedishHP:SVENSKA VARMMEPUMPE:Electrical Usage for Water Heating [W]'])
# ax.bar(x, df_march_cross['SwedishHP:SVENSKA VARMMEPUMPE:Electrical Usage for Water Heating [kWh]'])

plt.show()


# In[ ]:


df_march_self.shape


# In[ ]:


df_march_self['SwedishHP:SVENSKA VARMMEPUMPE:Source-side Heat Rate [W]']


# In[ ]:


df_march_cross['SwedishHP:SVENSKA VARMMEPUMPE:Source-side Heat Rate [kWh]']


# In[ ]:




