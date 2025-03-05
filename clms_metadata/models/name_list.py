from functools import cached_property, reduce
from pathlib import Path
from typing import Iterator, TypeVar

import yaml
from loguru import logger
from pydantic import BaseModel, Field

T = TypeVar("T")


class Instrument(BaseModel):
    instrumentName: str | None = None
    instrumentShortName: str | None = None


class Platform(BaseModel):
    platformName: str | None = None
    platformShortName: str | None = None
    platformAcronym: str | None = None
    alternativePlatformName: str | None = None
    instruments: list[Instrument] = Field(default_factory=list)

    def autocomplete(
        self,
        reference_traces: list[tuple["Mission", "Platform", Instrument]],
        instrument_short_names: list[str],
    ):
        common = get_common([rt[1] for rt in reference_traces])
        if common:
            if not self.platformName:
                self.platformName = common.platformName
            if not self.platformShortName:
                self.platformShortName = common.platformShortName
            if not self.platformAcronym:
                self.platformAcronym = common.platformAcronym
            if not self.alternativePlatformName:
                self.alternativePlatformName = common.alternativePlatformName
        if not self.instruments:
            if len(reference_traces) == 1:
                # just take the instrument
                self.instruments.append(reference_traces[0][2].model_copy())
            else:
                # add instruments if they occur in the provided list
                # first group instruments by instrumentShortName
                instruments = {
                    i.instrumentShortName: i
                    for rt in reference_traces
                    if (i := rt[2]).instrumentShortName in instrument_short_names
                }
                self.instruments.extend(i.model_copy() for i in instruments.values())
        if not self.instruments:
            # append empty instrument
            self.instruments.append(Instrument())


class Mission(BaseModel):
    missionName: str | None = None
    missionShortName: str | None = None
    platforms: list[Platform] = Field(default_factory=list)

    def autocomplete(
        self,
        reference_traces: list[tuple["Mission", Platform, Instrument]],
        instrument_short_names: list[str],
    ):
        common = get_common([rt[0] for rt in reference_traces])
        if common:
            if not self.missionName:
                self.missionName = common.missionName
            if not self.missionShortName:
                self.missionShortName = common.missionShortName
        if not self.platforms:
            # create empty platform and use common info of all traces
            platform = Platform()
            platform.autocomplete(reference_traces, instrument_short_names)
            self.platforms.append(platform)
        else:
            for platform in self.platforms:
                # autocomplete platform-specific information
                platform_reference_traces = [
                    rt
                    for rt in reference_traces
                    if rt[1].platformShortName == platform.platformShortName
                ]

                platform.autocomplete(platform_reference_traces, instrument_short_names)


class Program(BaseModel):
    programShortName: str | None = None
    missions: list[Mission] = Field(default_factory=list)


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
    ) -> Iterator[tuple[Mission, Platform, Instrument]]:
        """
        Method to look up values and retrieve all information that can be reliably derived from it.

        :param mission: mission short name
        :param platform: platform short name
        :param instrument: instrument short name
        :return: dictionary of attribute names to attribute values
        """
        # hits = defaultdict(dict)
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
                        yield obj_mission, obj_platform, obj_instrument


def autocomplete(
    missions: list[Mission],
    instrument_short_names: list[str],
    eo_asset_name_list: EOAssetNameList,
):
    """
    Using the EOAssetNameList, fill in the missing information in the provided missions.

    :param missions: list of missions
    :param instrument_short_names: list of instrument short names
    :param eo_asset_name_list: EOAssetNameList reference
    :return:
    """
    for mission in missions:
        logger.debug("Autocomplete mission: {}", mission)
        lookup_hits = []
        if mission.missionShortName is None:
            # lookup instrument names.
            for instrument in instrument_short_names:
                lookup_hits.extend(
                    hit
                    for hit in eo_asset_name_list.lookup(instrument=instrument)
                    if hit[0].missionShortName
                    not in (m.missionShortName for m in missions)
                )
        elif mission.platforms:
            for platform in mission.platforms:
                lookup_hits.extend(
                    eo_asset_name_list.lookup(
                        mission=mission.missionShortName,
                        platform=platform.platformShortName,
                    )
                )
        else:
            lookup_hits.extend(
                eo_asset_name_list.lookup(mission=mission.missionShortName)
            )

        mission.autocomplete(lookup_hits, instrument_short_names)
        logger.info(mission)
    logger.info("Autocomplete done!")


def get_common(models: list[T]) -> T:
    """
    Get the common attributes of a list of Pydantic models.
    The models should have the same type and allow None values for the attributes.

    :param models: list of models to reduce
    :return: model with the common attributes, or None if the list is empty
    """
    if len(models) == 0:
        return None
    t = type(models[0])

    def _common_dict(d1, d2) -> dict:
        return {k: v for k, v in d1.items() if k in d2 and d2[k] == v}

    common = reduce(_common_dict, map(lambda m: m.model_dump(), models))

    return t.model_validate(common)
