import os

import pandas as pd
from glhe.input_processor.component_types import ComponentTypes
from glhe.interface.entry import SimulationEntryPoint
from glhe.interface.response import SimulationResponse
from glhe.topology.ground_heat_exchanger_long_time_step import GroundHeatExchangerLTS
from glhe.topology.ground_heat_exchanger_short_time_step import GroundHeatExchangerSTS
from glhe.utilities.functions import merge_dicts


class GroundHeatExchanger(SimulationEntryPoint):
    Type = ComponentTypes.GroundHeatExchanger

    def __init__(self, inputs, ip, op):
        self.join = os.path.join
        self.norm = os.path.normpath

        SimulationEntryPoint.__init__(self, inputs)
        self.ip = ip
        self.op = op
        self.inputs = inputs

        try:
            self.sim_mode = self.inputs['simulation-mode']
        except KeyError:
            raise KeyError(
                "'simulation-mode' key not found")  # pragma: no cover

        if self.sim_mode == 'enhanced':
            # init TRCM model
            # g-function will be loaded or generated:
            self.sts_ghe = GroundHeatExchangerSTS(inputs, ip, op)

            # update g-function-path, if necessary:
            if 'g-function-path' not in self.inputs:
                # self.sts_ghe.generate_g()
                self.inputs['g-function-path'] = os.path.join(
                    self.op.output_dir, 'g.csv')
            # check for g_b-function and generate if necessary:
            if 'g_b-function-path' not in inputs:
                if 'g_b-flow-rates' not in inputs:
                    self.sts_ghe.generate_g_b()
                    self.inputs['g_b-function-path'] = os.path.join(
                        self.op.output_dir, 'g_b.csv')
                else:
                    if len(self.inputs['g_b-flow-rates']) > 1:
                        self._generate_multiple_g_b_function()
                    else:
                        self.sts_ghe.generate_g_b(inputs['g_b-flow-rate'])
                        self.inputs['g_b-function-path'] = os.path.join(
                            self.op.output_dir, 'g_b.csv')

            # init enhanced model
            d_bh_ave = self.sts_ghe.average_bh()
            lts_inputs = merge_dicts(inputs, {'length': self.sts_ghe.h,
                                              'number-boreholes': self.sts_ghe.num_bh,
                                              'average-borehole': d_bh_ave})

            self.lts_ghe = GroundHeatExchangerLTS(lts_inputs, ip, op)

            # alias functions based on sim mode
            self.simulate_time_step = self.lts_ghe.simulate_time_step
            self.report_outputs = self.lts_ghe.report_outputs

        elif self.sim_mode == 'direct':
            # init TRCM model only
            self.sts_ghe = GroundHeatExchangerSTS(inputs, ip, op)
            if 'g-function-path' not in inputs:
                self.sts_ghe.generate_g()
                inputs['g-function-path'] = os.path.join(
                    self.op.output_dir, 'g.csv')
            if 'g_b-function-path' not in inputs:
                if 'g_b-flow-rate' not in inputs:
                    self.sts_ghe.generate_g_b()
                    inputs['g_b-function-path'] = os.path.join(
                        self.op.output_dir, 'g.csv')
                else:
                    self.sts_ghe.generate_g_b(inputs['g_b-flow-rate'])
                    inputs['g_b-function-path'] = os.path.join(
                        self.op.output_dir, 'g.csv')

            # alias functions based on sim mode
            self.simulate_time_step = self.sts_ghe.simulate_time_step
            self.report_outputs = self.sts_ghe.report_outputs

        else:
            raise ValueError("Simulation mode '{}' is not valid".format(
                self.sim_mode))  # pragma: no cover

    def simulate_time_step(self, inputs: SimulationResponse):
        print("initialization was not successful.")
        pass  # pragma: no cover

    def report_outputs(self):
        pass  # pragma: no cover

    def _generate_g_function(self, write=True):
        """
        generate and save g function to the given directory (path)

        Parameters
        ----------
        write : boolean
            if write is True, the g function will be written to a file,
            else, it is just returned, without writing.


        Returns
        -------
        object GroundHeatExchangerSTS

        """

        return GroundHeatExchangerSTS(self.inputs,
                                      self.ip,
                                      self.op)

    def _generate_multiple_g_b_function(self):
        """
        generate and save g_b function to the given directory (path)

        Returns
        -------
        None.

        """

        flow_rates = self.inputs['g_b-flow-rates']
        g_b = pd.DataFrame(
            columns=flow_rates)

        # for-loop to generate a more-dimensional g_b function for multiple flow-rates
        i = 0
        for flow_rate in flow_rates:
            print("generating g_b function for a flow rate of {}".format(flow_rate))
            # this line will generate the files
            # g.csv
            # lts.csv
            # sts.csv
            # in the current projects folder:
            if i == 0:
                groundHEsts = self._generate_g_function()
                self.inputs['g-function-path'] = self.join(
                    self.op.output_dir, 'g.csv')
            else:
                groundHEsts = self._generate_g_function(write=False)
            groundHEsts.generate_g_b(flow_rate)
            g_b_current = [groundHEsts.lntts_b,
                           groundHEsts.g_b]
            g_b[flow_rate] = g_b_current[1]
            print("generated g_b function for a flow rate of {}".format(
                flow_rate))
            i += 1
        g_b.to_csv(self.join(self.op.output_dir, 'g_b.csv'), header=None)
        self.inputs['g_b-function-path'] = self.join(
            self.op.output_dir, 'g_b.csv')
