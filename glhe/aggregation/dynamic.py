from typing import Union

import numpy as np

from glhe.aggregation.agg_types import AggregationTypes
from glhe.aggregation.base_agg import BaseAgg
from glhe.aggregation.sub_hourly import SubHour
from glhe.utilities.constants import SEC_IN_HOUR


class Dynamic(BaseAgg):
    """
    Dynamic aggregation method.

    Claesson, J. and Javed, S. 2011. 'A load-aggregation method to calculate extraction temperatures
    of borehole heat exchangers.' ASHRAE Winter Conference, Chicago, IL. Jan. 21-25, 2012.
    """

    Type = AggregationTypes.DYNAMIC

    def __init__(self, inputs: dict):
        BaseAgg.__init__(self, inputs)

        # sub-hourly tracker for the first hour
        self.sub_hr = SubHour(inputs)

        # set expansion rate. apply default if needed.
        try:
            self.exp_rate = inputs['expansion-rate']
        except KeyError:  # pragma: no cover
            self.exp_rate = 1.62  # pragma: no cover

        # set the number of bins per level. apply default if needed.
        try:
            self.bins_per_level = inputs['number-bins-per-level']
        except KeyError:  # pragma: no cover
            self.bins_per_level = 9  # pragma: no cover

        # total simulation runtime to make available for method
        run_time = inputs['runtime']

        # time step for method
        # starts at 1 hr steps
        dt = SEC_IN_HOUR

        # method handles from hours 1 to n
        # the first hour (0 to 1) is handled by the sub-hourly method
        # these are referenced from the current simulation time
        t = SEC_IN_HOUR

        # initialize the dynamic method
        initialized = False
        while not initialized:
            for _ in range(self.bins_per_level):
                t += dt
                self.energy = np.insert(self.energy, 0, 0)
                self.dts = np.insert(self.dts, 0, dt)

                if t >= run_time:
                    initialized = True
                    break

            dt *= self.exp_rate

    def aggregate(self, time: int, energy: float):
        """
        Aggregate energy. Check for a new time step and aggregate.

        :param time: end sim time of energy value, in seconds. This should be the current sim time.
        :param energy: energy to be logged, in Joules
        """

        # check for iteration.
        # if time is the same as previous, we're iterating. so do nothing.
        # else, aggregate the energy
        if self.prev_update_time == time:
            return

        # run through sub-hourly method to track the first hour
        e_1 = self.sub_hr.aggregate(time, energy)

        # fraction of each bin's energy to shift for this time step
        # nothing is shifted out of final bin
        frac_shift = (time - self.prev_update_time) / self.dts
        frac_shift[0] = 0

        delta = self.energy * frac_shift
        self.energy = self.energy - delta
        self.energy = self.energy + np.roll(delta, -1)
        self.energy[-1] += e_1

        # update time
        self.prev_update_time = time

    def calc_temporal_superposition(self, time_step: int, flow_rate: float = None) -> Union[float, tuple]:

        # compute temporal superposition
        # this includes all thermal history before the present time
        lts_q = self.energy / self.dts
        sts_q = self.sub_hr.energy / self.sub_hr.dts
        q = np.concatenate((lts_q, sts_q))
        dq = np.diff(q, prepend=0)

        # g-function values
        dts = np.append(np.concatenate((self.dts, self.sub_hr.dts)), time_step)
        times = np.flipud(np.cumsum(np.flipud(dts)))[:-1]
        lntts = np.log(times / self.ts)
        g = self.interp_g(lntts)

        # convolution of delta_q and the g-function values
        if self.interp_g_b:
            # convolution for "g" and "g_b" g-functions
            if not flow_rate:
                g_b = self.interp_g_b(lntts)
            else:
                g_b = np.flipud(self.interp_g_b(lntts, flow_rate))
            return float(np.dot(dq, g)), float(np.dot(dq, g_b))
        else:
            # convolution for "g" g-functions only
            return float(np.dot(dq, g))

    def get_g_value(self, time_step: int) -> float:
        lntts = np.log(time_step / self.ts)
        return float(self.interp_g(lntts))

    def get_g_b_value(self, time_step: int, flow_rate: float = None) -> float:
        lntts = np.log(time_step / self.ts)
        if not flow_rate:
            return float(self.interp_g_b(lntts))
        else:
            return float(self.interp_g_b(lntts, flow_rate))

    def get_q_prev(self) -> float:
        return float(self.sub_hr.energy[-1] / self.sub_hr.dts[-1])
