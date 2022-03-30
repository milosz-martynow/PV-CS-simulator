from src.ReadConfig import ReadConfig
from src.Receiver import Receiver
from src.Sender import Sender
from datetime import datetime
import multiprocessing
from threading import Thread
import time
import sys
import os
import pandas as pd


class Simulator:

    def __init__(self):

        self.configs = ReadConfig()
        self.configs.load_toml()
        self.receiver = Receiver(PV_simulator_configs=self.configs.toml_dict["Photovoltaics"],
                                 run_setup=self.configs.toml_dict["RunSetup"])
        self.sender = Sender(meter_configs=self.configs.toml_dict["Meter"],
                             run_setup=self.configs.toml_dict["RunSetup"])

    def _sending_continuous_protocol(self):

        while True:
            message = datetime.now()
            self.sender.send(message)
            time.sleep(self.configs.toml_dict["RunSetup"]["sampling"])

    def _sending_date_range_protocol(self, times_pd: pd.core.indexes.datetimes.DatetimeIndex):

        for t in times_pd:
            message = t.to_pydatetime()
            self.sender.send(message)

    def run(self):

        try:

            p1 = multiprocessing.Process(name='p1', target=self.receiver.listening)
            p1.start()

            if self.configs.toml_dict["RunSetup"]["working_protocol"] == "Continuous":
                p2 = multiprocessing.Process(name='p2', target=self._sending_continuous_protocol)

            elif self.configs.toml_dict["RunSetup"]["working_protocol"] == "DateRange":
                times_pd = pd.date_range(start=self.configs.toml_dict["RunSetup"]["date_range_protocol_datetime_beg"],
                                         end=self.configs.toml_dict["RunSetup"]["date_range_protocol_datetime_end"],
                                         freq="{}S".format(self.configs.toml_dict["RunSetup"]["sampling"])).round("S")
                p2 = multiprocessing.Process(name='p2', target=self._sending_date_range_protocol, args=(times_pd,))
            p2.start()


        except KeyboardInterrupt:

            print('Interrupted')
            try:
                sys.exit(0)

            except SystemExit:
                os._exit(0)
