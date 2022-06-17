"""Test the Yamaha (YNCA) config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import (
    RESULT_TYPE_CREATE_ENTRY,
    RESULT_TYPE_FORM,
    RESULT_TYPE_MENU,
)

import custom_components.yamaha_ynca as yamaha_ynca
from ynca import YncaConnectionError

from .conftest import setup_integration


async def test_menu_form(hass: HomeAssistant) -> None:
    """Test we get the menu form when initialized by user."""

    result = await hass.config_entries.flow.async_init(
        yamaha_ynca.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == RESULT_TYPE_MENU


async def test_network_connect(hass: HomeAssistant) -> None:

    result = await hass.config_entries.flow.async_init(
        yamaha_ynca.DOMAIN, context={"source": "network"}
    )
    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] is None

    with patch(
        "ynca.Ynca.connection_check",
        return_value="ModelName",
    ) as mock_setup, patch(
        "custom_components.yamaha_ynca.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                yamaha_ynca.const.CONF_IP_ADDRESS: "192.168.1.123",
                yamaha_ynca.const.CONF_PORT: 12345,
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result2["title"] == "ModelName"
    assert result2["data"] == {
        yamaha_ynca.CONF_SERIAL_URL: "192.168.1.123:12345",
    }
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_advanced_connect(hass: HomeAssistant) -> None:

    result = await hass.config_entries.flow.async_init(
        yamaha_ynca.DOMAIN, context={"source": "advanced"}
    )
    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] is None

    with patch(
        "ynca.Ynca.connection_check",
        return_value="ModelName",
    ) as mock_setup, patch(
        "custom_components.yamaha_ynca.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                yamaha_ynca.CONF_SERIAL_URL: "SerialUrl",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result2["title"] == "ModelName"
    assert result2["data"] == {
        yamaha_ynca.CONF_SERIAL_URL: "SerialUrl",
    }
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        yamaha_ynca.DOMAIN, context={"source": "serial"}
    )

    with patch(
        "ynca.Ynca.connection_check",
        side_effect=YncaConnectionError("Connection error"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                yamaha_ynca.CONF_SERIAL_URL: "SerialUrl",
            },
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "cannot_connect_serial"}


async def test_form_unhandled_exception(hass: HomeAssistant) -> None:
    """Test we handle random exceptions."""
    result = await hass.config_entries.flow.async_init(
        yamaha_ynca.DOMAIN, context={"source": "serial"}
    )

    with patch(
        "ynca.Ynca.connection_check",
        side_effect=Exception("Unhandled exception"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                yamaha_ynca.CONF_SERIAL_URL: "SerialUrl",
            },
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "unknown_serial"}


async def test_options_flow(hass: HomeAssistant, mock_ynca) -> None:
    """Test optionsflow."""
    with patch(
        "ynca.get_all_zone_inputs",
        return_value={"INPUT_ID_1": "Input Name 1", "INPUT_ID_2": "Input Name 2"},
    ):
        integration = await setup_integration(hass, mock_ynca)

        result = await hass.config_entries.options.async_init(
            integration.entry.entry_id
        )

        assert result["type"] == RESULT_TYPE_FORM
        assert result["step_id"] == "init"

        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                yamaha_ynca.const.CONF_HIDDEN_INPUTS_FOR_ZONE("MAIN"): ["INPUT_ID_1"],
                yamaha_ynca.const.CONF_HIDDEN_INPUTS_FOR_ZONE("ZONE2"): ["INPUT_ID_2"],
            },
        )

        assert result["type"] == "create_entry"
        assert result["data"] == {
            yamaha_ynca.const.CONF_HIDDEN_INPUTS_FOR_ZONE("MAIN"): ["INPUT_ID_1"],
            yamaha_ynca.const.CONF_HIDDEN_INPUTS_FOR_ZONE("ZONE2"): ["INPUT_ID_2"],
            yamaha_ynca.const.CONF_HIDDEN_INPUTS_FOR_ZONE("ZONE3"): [],
            yamaha_ynca.const.CONF_HIDDEN_INPUTS_FOR_ZONE("ZONE4"): [],
        }
