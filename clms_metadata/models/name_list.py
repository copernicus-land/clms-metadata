from collections import defaultdict
from functools import cached_property
from pathlib import Path

import yaml
from loguru import logger
from pydantic import BaseModel

from clms_metadata.constants import attributes


class Instrument(BaseModel):
    instrumentName: str | None
    instrumentShortName: str | None


class Platform(BaseModel):
    platformName: str | None
    platformShortName: str | None
    platformAcronym: str | None
    alternativePlatformName: str | None
    instruments: list[Instrument]


class Mission(BaseModel):
    missionName: str | None
    missionShortName: str | None
    platforms: list[Platform]


class Program(BaseModel):
    programShortName: str | None
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

    @cached_property
    def missionShortNames(self) -> set[str]:
        return {
            m.missionShortName for program in self.EOasset for m in program.missions
        }

    @cached_property
    def platformShortNames(self) -> set[str]:
        return {
            p.platformShortName
            for program in self.EOasset
            for m in program.missions
            for p in m.platforms
        }

    @cached_property
    def platformAcronyms(self) -> set[str]:
        return {
            p.platformAcronym
            for program in self.EOasset
            for m in program.missions
            for p in m.platforms
        }

    @cached_property
    def instrumentShortNames(self) -> set[str]:
        return {
            i.instrumentShortName
            for program in self.EOasset
            for m in program.missions
            for p in m.platforms
            for i in p.instruments
        }

    def lookup(
        self,
        mission: str | None = None,
        platform: str | None = None,
        instrument: str | None = None,
    ) -> dict[str, str]:
        """
        Method to look up values and retrieve all information that can be reliably derived from it.

        :param mission: mission short name
        :param platform: platform short name
        :param instrument: instrument short name
        :return: dictionary of attribute names to attribute values
        """
        hits = defaultdict(set)
        # search for all matching values
        logger.info(
            "Lookup with parameters mission:{} platform:{} instrument:{}",
            mission,
            platform,
            instrument,
        )
        for obj_program in self.EOasset:
            logger.trace("Lookup for program '{}'", obj_program.programShortName)
            filtered_missions = filter(
                lambda m: mission is None or m.missionShortName == mission,
                obj_program.missions,
            )
            for obj_mission in filtered_missions:
                logger.trace("Lookup for mission '{}'", obj_mission.missionShortName)
                filtered_platforms = filter(
                    lambda p: platform is None or p.platformShortName == platform,
                    obj_mission.platforms,
                )
                for obj_platform in filtered_platforms:
                    logger.trace(
                        "Lookup for platform '{}'", obj_platform.platformShortName
                    )
                    filtered_instruments = filter(
                        lambda i: instrument is None
                        or i.instrumentShortName == instrument,
                        obj_platform.instruments,
                    )
                    for obj_instrument in filtered_instruments:
                        hits[attributes.MISSION_SHORT_NAME].add(
                            obj_mission.missionShortName
                        )
                        hits[attributes.PLATFORM_SHORT_NAME].add(
                            obj_platform.platformShortName
                        )
                        hits[attributes.PLATFORM_ACRONYM].add(
                            obj_platform.platformAcronym
                        )
                        hits[attributes.INSTRUMENT_SHORT_NAME].add(
                            obj_instrument.instrumentShortName
                        )

        # only keep attributes with a unique value
        result = dict()
        for key, value in hits.items():
            if len(value) == 1:
                [value] = value
                result[key] = value

        return result
