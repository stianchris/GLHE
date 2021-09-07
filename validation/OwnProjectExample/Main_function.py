#!/usr/bin/env python
# coding: utf-8
"""
Complete function to setup the simulation model from parameters.

"""

import os
import tempfile
import sys

import pandas as pd
import numpy as np
from datetime import datetime

from glhe.input_processor.input_processor import InputProcessor
from glhe.output_processor.output_processor import OutputProcessor
from glhe.topology.ground_heat_exchanger_short_time_step import GroundHeatExchangerSTS
from glhe.utilities.functions import write_json, load_json
from standalone.plant_loop import PlantLoop

import matplotlib.pyplot as plt


cwd = os.getcwd()
join = os.path.join
norm = os.path.normpath

# %%

f_in = 'own_project_input_1yr.json'
d = load_json(f_in)
ip = InputProcessor(f_in)
op = OutputProcessor('', 'out.csv')


# for-loop to generate a more-dimensional g_b function for multiple flow-rates
g_b = pd.DataFrame(columns=d['ground-heat-exchanger'][0]['g_b-flow-rates'])
for flow_rate in d['ground-heat-exchanger'][0]['g_b-flow-rates']:
    print("generating g_b function for a flow rate of {}".format(flow_rate))
    # this line will generate the files
    # g.csv
    # lts.csv
    # sts.csv
    # in the current projects folder:
    groundHEsts = GroundHeatExchangerSTS(d['ground-heat-exchanger'][0], ip, op)
    groundHEsts.generate_g_b(flow_rate)
    g_b_current = pd.read_csv(op.output_dir+'g_b.csv',
                              index_col=0, header=None)
    g_b[flow_rate] = g_b_current[1]
    print("generated g_b function for a flow rate of {}".format(flow_rate))
g_b.to_csv('g_b.csv', header=None)
# generate the paths to the files and add them to the json-file?
# --> is already in the run_sim file!

# In[ ]:

plt.style.use('seaborn-bright')
plt.rcParams['figure.figsize'] = [15, 9]
plt.rcParams['font.size'] = 12


# In[ ]:


sys.path.append(norm(join(cwd, '..', '..', '..', 'glhe')))


# In[ ]:


def run_sim(years_to_sim,
            json_path,
            loaddata_path,
            num_cross=None,
            years_to_delay_cross=None,
            dist_cross=None,
            testing=False,
            printing=False):

    d = load_json(json_path)
    print('loaded json file')

    d['ground-heat-exchanger'][0]['g-function-path'] = join(cwd, 'g.csv')
    d['ground-heat-exchanger'][0]['g_b-function-path'] = join(cwd, 'g_b.csv')
    # what is this for??
    # d['ground-heat-exchanger'][0]['g_b-flow-rates'] = [
    #     0.446
    # ],

    d['swedish-heat-pump'][0]['load-data-path'] = loaddata_path
    d['flow-profile'][0]['path'] = loaddata_path

    d['simulation']['runtime'] = 3600 * 24 * 365 * years_to_sim

    now = str(datetime.now())[0:16]

    f_in = 'in_{}-yr_self{}.json'.format(years_to_sim, now)
    f_out = 'out_{}-yr_self{}.csv'.format(years_to_sim, now)

    d['simulation']['output-csv-name'] = f_out
    d['simulation']['output-path'] = cwd

    write_json(f_in, d)
    print("start simulation.")
    PlantLoop(f_in).simulate(printing=printing)


# In[ ]:


run_sim(1,
        f_in,
        loaddata_path=join(cwd, 'HP_Loads_ODT.csv'),
        testing=False,
        printing=True)
# run_sim(20, testing=False)


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
            df_sums[col] = df_sums[col] / 1000

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
df_self = pd.read_csv('out_1-yr_self2021-07-12 12:27.csv',
                      index_col=0, parse_dates=True)
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


df_march_self = df_self.loc[df_self.index.month == 3]
# df_march_cross = df_cross.loc[df_cross.index.month==3]


# In[ ]:


fig = plt.figure()

ax = fig.add_subplot(111)

x = range(1, df_march_self.shape[0] + 1)

ax.bar(
    x, df_march_self['SwedishHP:SVENSKA VARMMEPUMPE:Electrical Usage for Water Heating [kWh]'])
ax.bar(
    x, df_march_cross['SwedishHP:SVENSKA VARMMEPUMPE:Electrical Usage for Water Heating [kWh]'])

plt.show()


# In[ ]:


df_march.shape


# In[ ]:


df_march_self['SwedishHP:SVENSKA VARMMEPUMPE:Source-side Heat Rate [kWh]']


# In[ ]:


df_march_cross['SwedishHP:SVENSKA VARMMEPUMPE:Source-side Heat Rate [kWh]']


# In[ ]:
