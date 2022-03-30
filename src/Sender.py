from src.SimulateDailyPowerConsumption import SimulateDailyPowerConsumption
from datetime import datetime
from json import dumps
from pika import BlockingConnection, ConnectionParameters


class Sender:

    def __init__(self, meter_configs: dict, run_setup: dict):

        self.meter_configs = meter_configs
        self.run_setup = run_setup

        self._meter_signature = SimulateDailyPowerConsumption(maximal_power=meter_configs["maximal_power_W"],
                                                              power_consumption_peak=meter_configs["power_consumption_peak_W"],
                                                              constant_power_consumption=meter_configs["constant_power_consumption_W"])
        self.message: str = None

    def _create_message_from_power_meter(self, meter_response_at_time: datetime.time):

        time_of_measurement = meter_response_at_time.time()
        power_consumption, over_range = self._meter_signature.calculate_signature_value_at_given_time(time_of_measurement)
        self.message = {"time_of_measurement": meter_response_at_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "power_consumption": power_consumption,
                        "over_range": over_range}
        self.message = dumps(self.message)

    def send(self, meter_response_at_time: datetime.time):

        self._create_message_from_power_meter(meter_response_at_time)
        connection = BlockingConnection(ConnectionParameters(host=self.run_setup["host"]))
        channel = connection.channel()
        channel.queue_declare(queue=self.run_setup["queue"])
        channel.basic_publish(exchange="", routing_key=self.run_setup["queue"], body=self.message)
        connection.close()
