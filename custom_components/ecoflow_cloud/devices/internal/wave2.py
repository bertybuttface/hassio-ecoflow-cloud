from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.components.climate.const import PRESET_ECO, PRESET_NONE, PRESET_SLEEP
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from custom_components.ecoflow_cloud.api import EcoflowApiClient
from custom_components.ecoflow_cloud.devices import BaseInternalDevice, const
from custom_components.ecoflow_cloud.entities import EcoFlowAbstractDataEntity
from custom_components.ecoflow_cloud.number import SetTempEntity
from custom_components.ecoflow_cloud.select import DictSelectEntity
from custom_components.ecoflow_cloud.sensor import (
    CapacitySensorEntity,
    LevelSensorEntity,
    MilliCelsiusSensorEntity,
    QuotaStatusSensorEntity,
    RemainSensorEntity,
    TempSensorEntity,
    WattsSensorEntity,
)


class Wave2(BaseInternalDevice):
    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # Power and Battery Entities
            LevelSensorEntity(client, self, "bms.soc", const.MAIN_BATTERY_LEVEL).attr(
                "bms.remainCap", const.ATTR_REMAIN_CAPACITY, 0
            ),
            CapacitySensorEntity(client, self, "bms.remainCap", const.MAIN_REMAIN_CAPACITY, False),
            TempSensorEntity(client, self, "bms.tmp", const.BATTERY_TEMP)
            .attr("bms.minCellTemp", const.ATTR_MIN_CELL_TEMP, 0)
            .attr("bms.maxCellTemp", const.ATTR_MAX_CELL_TEMP, 0),
            TempSensorEntity(client, self, "bms.minCellTmp", const.MIN_CELL_TEMP, False),
            TempSensorEntity(client, self, "bms.maxCellTmp", const.MAX_CELL_TEMP, False),
            RemainSensorEntity(client, self, "pd.batChgRemain", const.CHARGE_REMAINING_TIME),
            RemainSensorEntity(client, self, "pd.batDsgRemain", const.DISCHARGE_REMAINING_TIME),
            # heat pump
            MilliCelsiusSensorEntity(client, self, "pd.condTemp", "Condensation temperature", False),
            MilliCelsiusSensorEntity(client, self, "pd.heatEnv", "Return air temperature in condensation zone", False),
            MilliCelsiusSensorEntity(client, self, "pd.coolEnv", "Air outlet temperature", False),
            MilliCelsiusSensorEntity(client, self, "pd.evapTemp", "Evaporation temperature", False),
            MilliCelsiusSensorEntity(client, self, "pd.motorOutTemp", "Exhaust temperature", False),
            MilliCelsiusSensorEntity(client, self, "pd.airInTemp", "Evaporation zone return air temperature", False),
            TempSensorEntity(client, self, "pd.coolTemp", "Air outlet temperature", False),
            TempSensorEntity(client, self, "pd.envTemp", "Ambient temperature", False),
            # power (pd)
            WattsSensorEntity(client, self, "pd.mpptPwr", "PV input power"),
            WattsSensorEntity(client, self, "pd.batPwrOut", "Battery output power"),
            WattsSensorEntity(client, self, "pd.pvPower", "PV charging power"),
            WattsSensorEntity(client, self, "pd.acPwrIn", "AC input power"),
            WattsSensorEntity(client, self, "pd.psdrPower ", "Power supply power"),
            WattsSensorEntity(client, self, "pd.sysPowerWatts", "System power"),
            WattsSensorEntity(client, self, "pd.batPower ", "Battery power"),
            # power (motor)
            WattsSensorEntity(client, self, "motor.power", "Motor operating power"),
            # power (power)
            WattsSensorEntity(client, self, "power.batPwrOut", "Battery output power"),
            WattsSensorEntity(client, self, "power.acPwrI", "AC input power"),
            WattsSensorEntity(client, self, "power.mpptPwr ", "PV input power"),
            QuotaStatusSensorEntity(client, self),
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            SetTempEntity(
                client,
                self,
                "pd.setTemp",
                "Set Temperature",
                0,
                40,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "setTemp",
                    "sn": self.device_info.sn,
                    "params": {"setTemp": int(value)},
                },
            ),
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        return [
            DictSelectEntity(
                client,
                self,
                "pd.fanValue",
                const.FAN_MODE,
                const.FAN_MODE_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "fanValue",
                    "sn": self.device_info.sn,
                    "params": {"fanValue": value},
                },
            ),
            DictSelectEntity(
                client,
                self,
                "pd.mainMode",
                const.MAIN_MODE,
                const.MAIN_MODE_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "mainMode",
                    "sn": self.device_info.sn,
                    "params": {"mainMode": value},
                },
            ),
            DictSelectEntity(
                client,
                self,
                "pd.powerMode",
                const.REMOTE_MODE,
                const.REMOTE_MODE_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "powerMode",
                    "sn": self.device_info.sn,
                    "params": {"powerMode": value},
                },
            ),
            DictSelectEntity(
                client,
                self,
                "pd.subMode",
                const.POWER_SUB_MODE,
                const.POWER_SUB_MODE_OPTIONS,
                lambda value: {
                    "moduleType": 1,
                    "operateType": "subMode",
                    "sn": self.device_info.sn,
                    "params": {"subMode": value},
                },
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return []

    def climates(self, client: EcoflowApiClient) -> list[ClimateEntity]:
        return [Wave2ClimateEntity(client, self)]


class Wave2ClimateEntity(ClimateEntity, EcoFlowAbstractDataEntity):
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 1
    _attr_min_temp = 16
    _attr_max_temp = 30
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.FAN_ONLY]
    _attr_fan_modes = ["Low", "Medium", "High"]
    _attr_preset_modes = [PRESET_NONE, PRESET_ECO, PRESET_SLEEP, "Max"]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, client: EcoflowApiClient, device: BaseInternalDevice):
        super().__init__(client, device, "Air Conditioner", "climate")
        self._current_temperature: float | None = None
        self._target_temperature: float | None = None
        self._hvac_mode = HVACMode.OFF
        self._fan_mode = "Low"
        self._preset_mode = PRESET_NONE
        self._attr_available = True

    @property
    def current_temperature(self) -> float | None:
        return self._current_temperature

    @property
    def target_temperature(self) -> float | None:
        return self._target_temperature

    @property
    def hvac_mode(self) -> HVACMode:
        return self._hvac_mode

    @property
    def fan_mode(self) -> str | None:
        return self._fan_mode

    @property
    def preset_mode(self) -> str | None:
        return self._preset_mode

    def _handle_coordinator_update(self) -> None:
        if not self.coordinator.data.changed:
            return

        data = self.coordinator.data.data_holder.params
        if not data:
            return

        if "pd.tempSys" in data:
            if data["pd.tempSys"] == 1 and self._attr_temperature_unit != UnitOfTemperature.FAHRENHEIT:
                self._attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
                self._attr_min_temp = 60
                self._attr_max_temp = 86
            elif data["pd.tempSys"] == 0 and self._attr_temperature_unit != UnitOfTemperature.CELSIUS:
                self._attr_temperature_unit = UnitOfTemperature.CELSIUS
                self._attr_min_temp = 16
                self._attr_max_temp = 30

        if "pd.envTemp" in data:
            self._current_temperature = float(data["pd.envTemp"])

        if "pd.setTemp" in data:
            self._target_temperature = float(data["pd.setTemp"])

        power_mode = data.get("pd.powerMode")
        power_status = data.get("pd.powerSts")
        run_status = data.get("pd.runSts")
        main_mode = data.get("pd.mainMode") or data.get("pd.pdMainMode")

        if power_status is not None:
            device_is_on = power_status == 1
        elif run_status is not None:
            device_is_on = run_status > 0
        elif power_mode is not None:
            device_is_on = power_mode == 1
        else:
            device_is_on = False

        if not device_is_on:
            self._hvac_mode = HVACMode.OFF
        elif main_mode == 0:
            self._hvac_mode = HVACMode.COOL
        elif main_mode == 1:
            self._hvac_mode = HVACMode.HEAT
        elif main_mode == 2:
            self._hvac_mode = HVACMode.FAN_ONLY
        else:
            self._hvac_mode = HVACMode.OFF

        fan_value = data.get("pd.fanValue")
        if fan_value == 0:
            self._fan_mode = "Low"
        elif fan_value == 1:
            self._fan_mode = "Medium"
        elif fan_value == 2:
            self._fan_mode = "High"

        sub_mode = data.get("pd.pdSubMode") or data.get("pd.subMode")
        if sub_mode == 0:
            self._preset_mode = "Max"
        elif sub_mode == 1:
            self._preset_mode = PRESET_SLEEP
        elif sub_mode == 2:
            self._preset_mode = PRESET_ECO
        else:
            self._preset_mode = PRESET_NONE

        self._attr_available = any(
            key in data for key in ("pd.setTemp", "pd.powerMode", "pd.envTemp", "pd.runSts", "pd.powerSts")
        )
        self.schedule_update_ha_state()

    def _send_command(self, mqtt_key: str, value: Any, operate_type: str, param_name: str) -> None:
        command = {
            "moduleType": 1,
            "operateType": operate_type,
            "sn": self._device.device_info.sn,
            "params": {param_name: value},
        }
        adopted_key = f"'{mqtt_key}'" if self._device.flat_json() else mqtt_key
        self._client.send_set_message(self._device.device_info.sn, {adopted_key: value}, command)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TEMPERATURE in kwargs:
            self._send_command("pd.setTemp", int(kwargs[ATTR_TEMPERATURE]), "setTemp", "setTemp")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            self._send_command("pd.powerMode", 2, "powerMode", "powerMode")
            return
        self._send_command("pd.powerMode", 1, "powerMode", "powerMode")
        main_mode_value = {HVACMode.COOL: 0, HVACMode.HEAT: 1, HVACMode.FAN_ONLY: 2}.get(hvac_mode, 0)
        self._send_command("pd.mainMode", main_mode_value, "mainMode", "mainMode")

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        fan_value = {"Low": 0, "Medium": 1, "High": 2}.get(fan_mode, 0)
        self._send_command("pd.fanValue", fan_value, "fanValue", "fanValue")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        sub_mode_value = {"Max": 0, PRESET_SLEEP: 1, PRESET_ECO: 2}.get(preset_mode, 3)
        self._send_command("pd.subMode", sub_mode_value, "subMode", "subMode")

    async def async_turn_on(self) -> None:
        self._send_command("pd.powerMode", 1, "powerMode", "powerMode")

    async def async_turn_off(self) -> None:
        self._send_command("pd.powerMode", 2, "powerMode", "powerMode")
