from dataclasses import dataclass
from toml import load


@dataclass
class ReadConfig:

    config_name: str = "config.toml"
    toml_dict: dict = None

    def load_toml(self):

        self.toml_dict = load(self.config_name)
