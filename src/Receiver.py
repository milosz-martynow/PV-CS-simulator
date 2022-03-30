import pandas as pd
from src.SimulatePhotovoltaicCellGeneratedPower import SimulatePhotovoltaicCellGeneratedPower
from json import loads
from pika import BlockingConnection, ConnectionParameters
import matplotlib.pyplot as plt


class Receiver:

    def __init__(self, PV_simulator_configs: dict, run_setup: dict):

        self.PV_simulator_configs = PV_simulator_configs
        self.run_setup = run_setup

        self._PV_power_simulator = SimulatePhotovoltaicCellGeneratedPower(longitude_deg=self.PV_simulator_configs["longitude_deg"],
                                                                          latitude_deg=self.PV_simulator_configs["latitude_deg"],
                                                                          area_m2=self.PV_simulator_configs["area_m2"],
                                                                          efficiency=self.PV_simulator_configs["efficiency"])
        self._time_of_measurement: str = None
        self._measured_power_consumption: float = None
        self._simulated_PV_power: float = None
        self._power_difference: float = None
        self._data_summary: dict = {}
        self._data_summary_collection: list = []
        self._data_summary_df: pd.core.frame.DataFrame = None
        self._sampling_points: int = 1
        self._saving_time_beg: str = ""
        self._saving_time_end: str = ""

    def _plot(self):

        saving_pathname = "./results/{}_{}_{}.png".format(self.run_setup["naming_prefix"], self._saving_time_beg, self._saving_time_end)

        if self.run_setup["verbosity"] == "High":
            print("Plot will be saved in: {}".format(saving_pathname))

        fig, ax1 = plt.subplots(nrows=1, ncols=1)

        self._data_summary_df.plot(ax=ax1, y="Power consumption [kW]", linestyle="", marker="o", alpha=0.3)
        self._data_summary_df.plot(ax=ax1, y="Power generation [kW]", linestyle="", marker="s", alpha=0.3)
        self._data_summary_df.plot(ax=ax1, y="Power difference [kW]", linestyle="", marker="*", alpha=0.3)
        ax1.grid()

        fig.tight_layout()
        fig.savefig(saving_pathname, dpi=150)

    def _saving(self):

        saving_pathname = "./results/{}_{}_{}.csv".format(self.run_setup["naming_prefix"], self._saving_time_beg, self._saving_time_end)

        if self.run_setup["verbosity"] == "High":
            print("Data will be saved in: {}".format(saving_pathname))

        self._data_summary_df = pd.DataFrame(self._data_summary_collection)
        self._data_summary_df.set_index(keys=pd.DatetimeIndex(self._data_summary_df["Time [%Y-%m-%d %H:%M:%S]"]),
                                        inplace=True,
                                        drop=True)
        self._data_summary_df.to_csv(saving_pathname)

    def _closing(self):

        self._saving_time_beg = self._data_summary_collection[0]["Time [%Y-%m-%d %H:%M:%S]"]
        self._saving_time_end = self._data_summary_collection[-1]["Time [%Y-%m-%d %H:%M:%S]"]

        self._saving()
        if self.run_setup["plot"] is True:
            self._plot()

        self._sampling_points = 1
        self._data_summary_collection = []
        self._data_summary_df = None

        print("Data saved in results folder.")

    def _callback(self, ch, method, properties, body):

        message = body.decode("utf-8")
        message_dict = loads(message)
        self._measured_power_consumption = message_dict["power_consumption"]
        self._time_of_measurement = message_dict["time_of_measurement"]
        self._simulated_PV_power = self._PV_power_simulator.simulate_solar_power_on_PV(time_of_measurement=self._time_of_measurement)
        self._power_difference = self._measured_power_consumption - self._simulated_PV_power

        self._data_summary = {"Time [%Y-%m-%d %H:%M:%S]": self._time_of_measurement,
                              "Over range [bool]": message_dict["over_range"],
                              "Power consumption [kW]": self._measured_power_consumption,
                              "Power generation [kW]": self._simulated_PV_power,
                              "Power difference [kW]": self._power_difference}
        self._data_summary_collection.append(self._data_summary)

        if self.run_setup["verbosity"] == "High":
            print(self._data_summary)

        if self.run_setup["working_protocol"] == "Continuous":

            if self._sampling_points < self.run_setup["continuous_protocol_lines_to_save"]:
                self._sampling_points += 1
            else:
                self._closing()

        if self.run_setup["working_protocol"] == "DateRange":

            times_pd = pd.date_range(start=self.run_setup["date_range_protocol_datetime_beg"],
                                     end=self.run_setup["date_range_protocol_datetime_end"],
                                     freq="{}S".format(self.run_setup["sampling"])).round("S")
            number_of_measurements = len(times_pd)

            if self._sampling_points < number_of_measurements:
                self._sampling_points += 1
            else:
                self._closing()

    def listening(self):

        connection = BlockingConnection(ConnectionParameters(host=self.run_setup["host"]))
        channel = connection.channel()
        channel.queue_declare(queue=self.run_setup["queue"])
        channel.basic_consume(queue=self.run_setup["queue"], on_message_callback=self._callback, auto_ack=True)
        channel.start_consuming()

