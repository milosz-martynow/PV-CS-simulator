from dataclasses import dataclass
from datetime import datetime
from pandas import date_range
from pvlib.location import Location


@dataclass
class SimulatePhotovoltaicCellGeneratedPower:

    latitude_deg: float = None
    longitude_deg: float = None
    area_m2: float = None
    efficiency: float = None

    def simulate_solar_power_on_PV(self, time_of_measurement: str):

        time_of_measurement = datetime.strptime(time_of_measurement, "%Y-%m-%d %H:%M:%S")
        time_of_measurement = date_range(start=time_of_measurement, end=time_of_measurement, periods=1).round("S")

        #  Model assumes that:
        #  1. We have clear sky
        #  2. Sunlight appear on the photovoltaic panel perpendicular
        #  All those assumptions can be avoided, even by pvlib - but this is basic model
        solar_irradiance = Location(longitude=self.longitude_deg, latitude=self.latitude_deg)
        solar_power = solar_irradiance.get_clearsky(time_of_measurement)["dni"] * self.area_m2 * self.efficiency / 1000
        solar_power = solar_power.values[0]

        return solar_power
