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
            path = self.cwd

        # read in the json file
        self.d = load_json(path+"/"+input_json_file)
        self.ip = InputProcessor(path+"/"+input_json_file)
        self.op = OutputProcessor(path, 'out.csv')
        
        # create GroundHeatExchanger object
        self.ghe = GroundHeatExchanger(self.d['ground-heat-exchanger'][0],
                                       self.ip,
                                       self.op)

        # operation variables
        self.time = 0
        self.timestep = 0
        self.flow_rate = 0
        self.temperature = 0
        self.temp_out = 0


    def operate_btes(self,
                     time=None,
                     time_step=None,
                     flow_rate=None,
                     temperature=None):
        """
        Operates the btes for one time step and stores the outputs

        Outputs are stored in self.temp_out for the output temperature.

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
        if time == None:
            time = self.time
        else:
            self.time = time

        if time_step == None:
            time_step = self.time_step
        else:
            self.time_step = time_step

        if flow_rate == None:
            flow_rate = self.flow_rate
        else:
            self.flow_rate = flow_rate

        if temperature == None:
            temperature = self.temperature
        else:
            self.temperature = temperature

        # for debugging:
        # print("time:",str(time))
        # print("time_step:",str(time_step))
        # print("flow_rate:",str(flow_rate))
        # print("temperature:",str(temperature))
        inputs = SimulationResponse(time,
                                    time_step,
                                    flow_rate,
                                    temperature)
        outputs = self.ghe.simulate_time_step(inputs)
        # print(outputs.temperature)

        self.temp_out = outputs.temperature

        return outputs


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
    test_dir = "test_files"
    btes = BTES_interface("test_file.json", join(cwd,"..", test_dir))

    now = str(datetime.now())[0:16]
    years_to_sim = 1

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
