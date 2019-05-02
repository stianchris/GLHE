import os
from abc import ABC, abstractmethod

import numpy as np
from scipy.interpolate import interp1d

join = os.path.join
norm = os.path.normpath
cwd = os.getcwd()


class BaseAgg(ABC):

    def __init__(self, inputs: dict):
        # g-function values
        if 'g-function-path' in inputs:
            path = norm(join(cwd, inputs['g-function-path']))
            data = np.genfromtxt(path, delimiter=',')
        elif 'lntts' in inputs:
            data = np.transpose(np.array([inputs['lntts'], inputs['g-values']]))
        else:
            raise KeyError('g-function data not found.')
        self.interp_g = interp1d(data[:, 0], data[:, 1], fill_value='extrapolate')
        self.ts = inputs['time-scale']

        # energy values to be tracked
        self.energy = np.empty((0,), dtype=float)

        # most recent values appended to array
        self.times = np.empty((0,), dtype=int)

        # time step of each respective bin
        self.dts = np.empty((0,), dtype=int)

        # g-function values for each respective bin
        self.g_vals = np.empty((0,), dtype=float)

        # previous time the aggregation method was updated
        self.prev_update_time = None

    @abstractmethod
    def aggregate(self, time: int, energy: float):
        pass  # pragma: no cover

    @abstractmethod
    def calc_superposition_coeffs(self, time: int, time_step: int) -> tuple:
        pass  # pragma: no cover
