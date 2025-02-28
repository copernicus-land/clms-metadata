from pathlib import Path

import yaml
from pydantic import BaseModel


class Instrument(BaseModel):
    instrumentName: str
    instrumentShortName: str


class Platform(BaseModel):
    platformName: str
    platformShortName: str
    platformAcronym: str
    alternativePlatformName: str
    instruments: list[Instrument]


class Mission(BaseModel):
    missionName: str
    missionShortName: str
    platforms: list[Platform]


class Program(BaseModel):
    programShortName: str
    missions: list[Mission]


class EOAssetNameList(BaseModel):
    EOasset: list[Program]

    @classmethod
    def from_yaml(cls, path: Path):
        """
        Load an EOAssetNameList from a YAML file.

        :param path: path of the YAML file to read
        :return: EOAssetNameList object
        """

        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
