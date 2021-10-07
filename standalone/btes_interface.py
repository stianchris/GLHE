#!/usr/bin/env python
# coding: utf-8
"""
An integration of the GLHE package from Matt Mitchell (2018).

"""

import os
import tempfile
import sys

import pandas as pd
import numpy as np
from datetime import datetime

from glhe.input_processor.input_processor import InputProcessor
from glhe.input_processor.component_types import ComponentTypes
from glhe.output_processor.output_processor import OutputProcessor
from glhe.topology.ground_heat_exchanger_short_time_step import GroundHeatExchangerSTS
from glhe.topology.ground_heat_exchanger import GroundHeatExchanger
from glhe.utilities.functions import write_json, load_json
from standalone.plant_loop import PlantLoop
from glhe.interface.response import SimulationResponse


class BTES_interface(object):
    Type = ComponentTypes.BTES_interface

    def __init__(self, input_json_file, path=""):
        """
        Interface to use GLHE in energysystem simulation.

        This interface requires a json input-file as described in the examples.
        It initializes a GLHE object and provides a function to operate it 
        with single time-steps as a borehole thermal energy storage (BTES).
        
        Parameters
        ----------
        input_json_file : string
            Name of the json file to be used as input for the initialization
            of the GLHE.
        path : string
            optional path to the json-file. Defaults to the current working
            directory.

        Returns
        -------
        None.
        """
        self.cwd = os.getcwd()
        self.join = os.path.join
        self.norm = os.path.normpath
        if path == "":
            path = cwd

        # read in the json file
        self.d = load_json(path+"/"+input_json_file)
        self.ip = InputProcessor(path+"/"+input_json_file)
        self.op = OutputProcessor(path, 'out.csv')
        
        # create GroundHeatExchanger object
        self.ghe = GroundHeatExchanger(self.d['ground-heat-exchanger'][0],
                                       self.ip,
                                       self.op)


    def operate_btes(self, time, time_step, flow_rate, temperature):
        """


        Parameters
        ----------
        time : float
            actual time step in seconds
        time_step : float
            length of each time step in seconds
        temperature : float
            temperature input into the borehole
        flow_rate : float
            flow-rate input into the borehole

        Returns
        -------
        None.

        """
        # prepare inputs!!
        inputs = SimulationResponse(time,
                                    time_step,
                                    flow_rate,
                                    temperature)
        return self.ghe.simulate_time_step(inputs)


    def run_sim(self,
                years_to_sim,
                json_path,
                loaddata_path,
                num_cross=None,
                years_to_delay_cross=None,
                dist_cross=None,
                testing=False,
                printing=False,
                add_id=False):
        """
        Just for testing. Not finished yet.

        Parameters
        ----------
        years_to_sim : TYPE
            DESCRIPTION.
        json_path : TYPE
            DESCRIPTION.
        loaddata_path : TYPE
            DESCRIPTION.
        num_cross : TYPE, optional
            DESCRIPTION. The default is None.
        years_to_delay_cross : TYPE, optional
            DESCRIPTION. The default is None.
        dist_cross : TYPE, optional
            DESCRIPTION. The default is None.
        testing : TYPE, optional
            DESCRIPTION. The default is False.
        printing : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None.

        """
        d = load_json(json_path)
        print('loaded json file')

        d['ground-heat-exchanger'][0]['g-function-path'] = self.join(
            self.cwd, 'test/g.csv')
        d['ground-heat-exchanger'][0]['g_b-function-path'] = self.join(
            self.cwd, 'test/g_b.csv')
        # what is this for??
        # d['ground-heat-exchanger'][0]['g_b-flow-rates'] = [
        #     0.446
        # ],

        d['swedish-heat-pump'][0]['load-data-path'] = loaddata_path
        d['flow-profile'][0]['path'] = loaddata_path

        d['simulation']['runtime'] = 3600 * 24 * 365 * years_to_sim

        if add_id:
            now = add_id
        else:
            now = ""

        f_in = 'in_{}-yr_self{}.json'.format(years_to_sim, now)
        f_out = 'out_{}-yr_self{}.csv'.format(years_to_sim, now)

        d['simulation']['output-csv-name'] = f_out
        d['simulation']['output-path'] = self.join(
            self.cwd, "test")

        write_json(f_in, d)
        print("start simulation.")
        self.pl = PlantLoop(f_in)
        self.pl.simulate(printing=printing)


# %%
if __name__ == "__main__":
    cwd = os.getcwd()
    join = os.path.join
    test_dir = "test"
    btes = BTES_interface("test_file.json", join(cwd, test_dir))

    # %% test von simulation run - grundsätzliche Funktion.
    now = str(datetime.now())[0:16]
    years_to_sim = 1
    # btes.run_sim(years_to_sim,
    #               json_path=join(cwd, test_dir, "test_file.json"),
    #               loaddata_path=join(cwd, test_dir, "HP_Loads_ODT.csv"),
    #               add_id=now)
    # df_self = pd.read_csv(
    #     join(test_dir, 'out_{}-yr_self{}.csv'.format(years_to_sim, now)),
    #     index_col=0, parse_dates=True)
    # test Ergebnisse der Simu plotten
    # fig = plt.figure()

    # ax = fig.add_subplot(111)

    # cols = [
    #     # 'GroundHeatExchangerLTS:SELF-GHE:BH Resist. [m-K/W]',
    #     # 'GroundHeatExchangerLTS:SELF-GHE:Heat Rate [W]',
    #     'GroundHeatExchangerLTS:SELF-GHE:Inlet Temp. [C]',
    #     'GroundHeatExchangerLTS:SELF-GHE:Outlet Temp. [C]',
    #     # 'SwedishHP:SVENSKA VARMMEPUMPE:COP [-]',
    #     'SwedishHP:SVENSKA VARMMEPUMPE:Outdoor Air Temp. [C]',
    #     # 'SwedishHP:SVENSKA VARMMEPUMPE:Load-side Heat Rate [W]',
    #     # 'PlantLoop:Demand Inlet Temp. [C]',
    #     # 'PlantLoop:Demand Outlet Temp. [C]',
    #     # 'PlantLoop:Supply Inlet Temp. [C]',
    #     # 'PlantLoop:Supply Outlet Temp. [C]',
    #     # 'ConstantFlow:CONSTANT FLOW:Flow Rate [kg/s]',
    #     # 'SwedishHP:SVENSKA VARMMEPUMPE:Outlet Temp. [C]',
    #     # 'SwedishHP:SVENSKA VARMMEPUMPE:Inlet Temp. [C]',
    #     # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Heat Rate [W]',
    #     # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:BH Heat Rate [W]',
    #     # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Inlet Temp. [C]',
    #     # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Outlet Temp. [C]',
    #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Inlet Temp. Leg 1 [C]',
    #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Inlet Temp. Leg 2 [C]',
    #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Outlet Temp. Leg 1 [C]',
    #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Outlet Temp. Leg 2 [C]',
    #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:2:Outlet Temp. [C]',
    # ]

    # for col in cols:
    #     ax.plot(df_self[col], label=col)
    #     # ax.plot(df_cross[col], label=col+"cross")

    # plt.legend()
    # plt.show()

    # %%
    # test von operate_btes:
    ser = []
    # time_index = 
    i_list = [0,1,10,50,100,500,1000,1500,2000]
    for i in range(24 * 365 * years_to_sim):
        # i = i+1
        if i in i_list:
            params = btes.operate_btes((i)*3600, 3600, 0.446, 10)
            print(params.temperature)
            ser.append(params.temperature)
        else:
            temp = btes.ghe.lts_ghe.bh_wall_temperature
            params = btes.operate_btes((i)*3600, 3600, 0.446, temp)
            print(params.temperature)
            ser.append(params.temperature)


# TODO: HP-Load profile ersetzen mit eigenem!
#       Test der Einbindung in Gesamtmodell! Mit anderen Bibliotheken..
