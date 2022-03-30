from dataclasses import dataclass
from datetime import datetime

from numpy import pi, cos, exp


@dataclass
class SimulateDailyPowerConsumption:

    maximal_power: float = 9000
    power_consumption_peak: float = 7000
    constant_power_consumption: float = 200

    _timestamp_total_seconds: float = None
    _two_pi_range_val: float = None
    _power_consumption: float = None
    _over_range: int = None

    def _convert_time_to_total_seconds(self, timestamp):

        self._timestamp_total_seconds = (timestamp.hour * 60 + timestamp.minute) * 60 + timestamp.second

    def _convert_time_to_0_2pi_range(self):

        self._timestamp_total_seconds = self._timestamp_total_seconds / 86400
        self._two_pi_range_val = 2 * pi * self._timestamp_total_seconds

    @staticmethod
    def _normal_distribution(x: float, mean: float, std: float) -> float:

        y = exp(-0.5 * ((x - mean) / std)**2)

        return y

    def _signature_function(self):

        #  Casual day consumption
        self._power_consumption = -1 * cos(self._two_pi_range_val) * self.power_consumption_peak

        #  Add out of meter range consumption peak
        peak = self._normal_distribution(x=self._two_pi_range_val, mean=1.2 * pi, std=0.01 * pi)
        peak = 1.01 * self.maximal_power * peak
        self._power_consumption = self._power_consumption + peak

    def _filter_over_range(self):

        self._over_range = 0

        if self._power_consumption < self.constant_power_consumption:
            self._power_consumption = self.constant_power_consumption

        if self._power_consumption > self.maximal_power:
            self._power_consumption = self.maximal_power
            self._over_range = 1

        self._power_consumption = self._power_consumption / 1000

    def calculate_signature_value_at_given_time(self, timestamp: datetime.time):

        self._convert_time_to_total_seconds(timestamp=timestamp)
        self._convert_time_to_0_2pi_range()
        self._signature_function()
        self._filter_over_range()

        return self._power_consumption, self._over_range
