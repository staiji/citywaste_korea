"""Support for getting statistical data from a city-waste system."""
import datetime
from datetime import timedelta
import json
import logging

import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_MONITORED_CONDITIONS, CONF_NAME, MASS_KILOGRAMS
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_TAGPRINTCD = "tagprintcd"
CONF_APTDONG = "aptdong"
CONF_APTHONO = "apthono"
DEFAULT_NAME = "Citywaste"

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)

MONITORED_CONDITIONS = {
    "total_count": ["Total count", " ", "mdi:counter"],
    "last_kg": ["Last kg", MASS_KILOGRAMS, "mdi:scale"],
    "last_date": ["Last date", " ", "mdi:calendar-clock"],
    "total_kg": ["Total kg", MASS_KILOGRAMS, "mdi:scale"],
    "address": ["Address", " ", "mdi:home"],
}

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_TAGPRINTCD): cv.string,
        vol.Required(CONF_APTDONG): cv.positive_int,
        vol.Required(CONF_APTHONO): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(
            CONF_MONITORED_CONDITIONS, default=["total_kg", "total_count", "last_kg"]
        ): vol.All(cv.ensure_list, [vol.In(MONITORED_CONDITIONS)]),
    }
)

BASE_URL = (
    "https://www.citywaste.or.kr/portal/status/selectDischargerQuantityQuickMonthNew.do"
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    name = config.get(CONF_NAME)
    tagprintcd = config.get(CONF_TAGPRINTCD)
    aptdong = config.get(CONF_APTDONG)
    apthono = config.get(CONF_APTHONO)
    cwdata = CityWasteData(tagprintcd, aptdong, apthono)

    sensors = [
        CityWasteSensor(cwdata, name, condition)
        for condition in config[CONF_MONITORED_CONDITIONS]
    ]

    add_entities(sensors)


class CityWasteSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, cwdata, name, condition):
        """Initialize the sensor."""
        self.cwdata = cwdata
        self._name = name
        self._condition = condition

        variable_info = MONITORED_CONDITIONS[condition]
        self._condition_name = variable_info[0]
        self._unit_of_measurement = variable_info[1]
        self._icon = variable_info[2]
        self.data = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{} {}".format(self._name, self._condition_name)

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def state(self):
        """Return the state of the device."""
        try:
            return round(self.data[self._condition], 2)
        except TypeError:
            return self.data[self._condition]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self._condition == "total_kg":
            return {
                "address": self.data["address"],
                "total_count": self.data["total_count"],
                "last_kg": round(self.data["last_kg"], 2),
                "last_date": self.data["last_date"],
                "total_kg": round(self.data["total_kg"], 2),
            }

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self.cwdata.available

    def update(self):
        """Fetch new state data for the sensor.
        
        This is the only method that should fetch new data for Home Assistant.
        """
        self.cwdata.update()
        self.data = self.cwdata.data


class CityWasteData:
    """Get the latest data and update the states."""

    def __init__(self, tagprintcd, aptdong, apthono):
        """Initialize the data object."""
        self.tagprintcd = tagprintcd
        self.aptdong = aptdong
        self.apthono = apthono
        self.data = {}

        self.available = False

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from the City waste."""
        totalkg = 0
        lastkg = 0
        totalPageCount = 0

        self.available = False

        now = datetime.datetime.now()
        firstDate = now.strftime("%Y%m01")
        nowDate = now.strftime("%Y%m%d")
        API_URL = (
            BASE_URL
            + f"?tagprintcd={self.tagprintcd}&aptdong={self.aptdong}&apthono={self.apthono}&startchdate={firstDate}&endchdate={nowDate}"
        )
        REQ_URL = API_URL + "&pageIndex=1"
        _LOGGER.info("REQ_URL %s", REQ_URL)

        try:
            res = requests.get(REQ_URL)
            if res.status_code == 404:
                _LOGGER.info("retrying one more time for 1st page")
                res = requests.get(URL)

            res.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            _LOGGER.error("Http Error: %s", errh)
            return
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.error("Error Connecting: %s", errc)
            return
        except requests.exceptions.Timeout as errt:
            _LOGGER.error("Timeout Error: %s", errt)
            return

        if res.status_code == 200:
            try:
                totalCnt = res.json()["totalCnt"]
                totalPageCount = res.json()["paginationInfo"]["totalPageCount"]
                address = res.json()["ctznnm"]
                list = res.json()["list"]

                if len(list) > 0:
                    lastkg = list[0]["qtyvalue"]
                    lastdate = list[0]["dttime"]
                    for i in list:
                        totalkg += i["qtyvalue"]

            except ValueError as err:
                _LOGGER.error("Error parsing json %s", err)
                return
            except:
                _LOGGER.error("Error parsing list")
                return
        else:
            _LOGGER.error("First request status_code %s", res.status_code)
            return

        if totalPageCount > 1:
            for currentPage in range(2, totalPageCount + 1):
                try:
                    REQ_URL = API_URL + "&pageIndex=" + str(currentPage)
                    _LOGGER.info("REQ_URL %s", REQ_URL)
                    res = requests.get(REQ_URL)
                    if res.status_code == 404:
                        _LOGGER.info("retrying one more time for page %s", currentPage)
                        res = requests.get(REQ_URL)

                    res.raise_for_status()
                except requests.exceptions.HTTPError as errh:
                    _LOGGER.error("Http Error: %s", errh)
                    return
                except requests.exceptions.ConnectionError as errc:
                    _LOGGER.error("Error Connecting: %s", errc)
                    return
                except requests.exceptions.Timeout as errt:
                    _LOGGER.error("Timeout Error: %s", errt)
                    return

                if res.status_code == 200:
                    try:
                        list = res.json()["list"]
                        if len(list) > 0:
                            for i in list:
                                totalkg += i["qtyvalue"]
                    except ValueError as err:
                        _LOGGER.error("Error parsing json %s", err)
                        return
                    except:
                        _LOGGER.error("Error parsing list")
                        return
                else:
                    _LOGGER.error("Second request status_code %s", res.status_code)
                    return

        _LOGGER.info(
            "totalkg %s total_count %s last_kg %s", totalkg, totalCnt, lastkg
        )
        self.available = True
        self.data["total_count"] = totalCnt
        self.data["last_kg"] = lastkg
        self.data["last_date"] = lastdate
        self.data["total_kg"] = totalkg
        self.data["address"] = address
