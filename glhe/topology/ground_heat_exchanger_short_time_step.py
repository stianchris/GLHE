from glhe.input_processor.component_types import ComponentTypes
from glhe.input_processor.input_processor import InputProcessor
from glhe.interface.entry import SimulationEntryPoint
from glhe.interface.response import SimulationResponse
from glhe.output_processor.output_processor import OutputProcessor
from glhe.output_processor.report_types import ReportTypes
from glhe.topology.path import Path


class GroundHeatExchangerSTS(SimulationEntryPoint):
    Type = ComponentTypes.GroundHeatExchangerSTS

    def __init__(self, inputs: dict, ip: InputProcessor, op: OutputProcessor):
        SimulationEntryPoint.__init__(self, inputs)
        self.ip = ip
        self.op = op

        # init paths
        self.paths = []
        for path in inputs['flow-paths']:
            self.paths.append(Path(path, ip, op))

        # report variables
        self.heat_rate = 0
        self.flow_rate = 0
        self.inlet_temperature = ip.init_temp()
        self.outlet_temperature = ip.init_temp()

    def calc_ave_depth(self):
        valid_bh_types = [ComponentTypes.BoreholeSingleUTubeGrouted]
        ave_depth = 0
        count = 0
        for path in self.paths:
            for comp in path.components:
                if comp.Type in valid_bh_types:
                    ave_depth += comp.depth
                    count += 1

        return ave_depth / count

    def count_bhs(self):
        valid_bh_types = [ComponentTypes.BoreholeSingleUTubeGrouted]
        count = 0
        for path in self.paths:
            for comp in path.components:
                if comp.Type in valid_bh_types:
                    count += 1

        return count

    def simulate_time_step(self, inputs: SimulationResponse):
        return inputs

    def report_outputs(self):
        return {'{:s}:{:s}:{:s}'.format(self.Type, self.name, ReportTypes.HeatRate): self.heat_rate,
                '{:s}:{:s}:{:s}'.format(self.Type, self.name, ReportTypes.FlowRate): self.flow_rate,
                '{:s}:{:s}:{:s}'.format(self.Type, self.name, ReportTypes.InletTemp): self.inlet_temperature,
                '{:s}:{:s}:{:s}'.format(self.Type, self.name, ReportTypes.OutletTemp): self.outlet_temperature}
