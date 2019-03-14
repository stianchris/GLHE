#!/usr/bin/env python3

import sys

from glhe.globals.functions import num_ts_per_hour_to_sec_per_ts
from glhe.inputProcessor.input_processor import InputProcessor
from glhe.outputProcessor.output_processor import OutputProcessor
from glhe.profiles.flow_factory import make_flow_profile
from glhe.profiles.load_factory import make_load_profile
from glhe.topology.full_ground_loop import GLHE


class PlantLoop(object):
    """
    Do a plant loop simulation.  Responsibilities include:
    1. Get Inputs for the whole plant loop
    2. Instantiate components
    3. Setup topology, connections
    4. Initialize the loop
    5. Simulate the loop flow-wise
    6. Control?
    """

    def __init__(self, json_file_path: str):
        """
        
        :param json_file_path: Path to the JSON input file
        """
        self.ip = InputProcessor()
        self.inputs = self.ip.process_input(json_file_path)
        self.op = OutputProcessor()
        self.flow_profile = make_flow_profile(self.inputs['flow-profile'])
        self.load_profile = make_load_profile(self.inputs['load-profile'])
        self.fluid = self.ip.props_mgr.fluid
        self.soil = self.ip.props_mgr.soil
        self.glhe = GLHE(self.inputs, self.ip, self.op)
        init_temp = self.ip.gtm.get_temp(0, 100)
        self.demand_inlet_temperature = init_temp
        self.demand_outlet_temperature = init_temp
        self.supply_inlet_temperature = init_temp
        self.supply_outlet_temperature = init_temp
        self.flow_rate = 0.0
        self.load = 0.0

    def simulate(self) -> bool:
        """
        Do the entire time stepping simulation of the plant loop
        
        :return: True if successful, False if not
        """
        time_step = num_ts_per_hour_to_sec_per_ts(self.inputs['simulation']['time-steps per hour'])
        end_sim_time = self.inputs['simulation']['runtime']
        current_sim_time = 0
        while True:
            end_of_this_time_step = current_sim_time + time_step
            if not self.do_one_time_step(current_sim_time):
                return False
            if end_of_this_time_step >= end_sim_time:
                break
            current_sim_time = end_of_this_time_step

            self.op.collect_output({'Time': current_sim_time,
                                    'Demand Inlet Temperature': self.demand_inlet_temperature,
                                    'Demand Outlet Temperature': self.demand_outlet_temperature,
                                    'Supply Inlet Temperature': self.supply_inlet_temperature,
                                    'Supply Outlet Temperature': self.supply_outlet_temperature,
                                    'Plant Flow Rate': self.flow_rate,
                                    'Plant Load': self.load})

        return True

    def do_one_time_step(self, current_sim_time: int) -> bool:
        """
        Simulate one time step of the entire plant loop
        Consists of:
        
        - Adding a load
        - Looping over components
        
        :return: True if successful, False if not
        """

        self.flow_rate = self.flow_profile.get_value(current_sim_time)
        self.load = self.load_profile.get_value(current_sim_time)

        # Simulate demand side
        demand_cp = self.fluid.calc_specific_heat(self.demand_inlet_temperature)
        self.demand_outlet_temperature = self.demand_inlet_temperature + self.load / (self.flow_rate * demand_cp)
        # Simulate supply side
        self.supply_inlet_temperature = self.demand_outlet_temperature  # could do mass here?
        # TODO: Fix GLHE so we can call it
        import random
        self.supply_outlet_temperature = 18 + float(random.randint(1, 100)) / 50
        # self.supply_outlet_temperature = self.glhe.simulate_time_step(
        #     self.supply_inlet_temperature, self.flow_rate, current_sim_time
        # )
        # Advance time
        self.demand_inlet_temperature = self.supply_outlet_temperature  # could do mass here
        return True


if __name__ == "__main__":
    PlantLoop(sys.argv[1]).simulate()
