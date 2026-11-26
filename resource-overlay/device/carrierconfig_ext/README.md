# CarrierConfig Overlay Extension

## Overview

This package provides a device-specific extension for Motorola's CarrierConfig overlay.

It allows device maintainers and contributors to add or customize carrier configurations without directly modifying Motorola's original `vendor.xml`.

Carrier-specific settings are merged into the corresponding Motorola carrier entries. Existing Motorola settings are preserved, while device-specific values take precedence when the same key is defined in both configurations.

## Directory Structure

- `carriers/` — Individual carrier configuration XML files.
- `gen_carrier_config.py` — Script responsible for merging carrier configurations.
- `carrierconfig_ext.mk` — Build integration and generated-file validation.
- `rro/` — Runtime Resource Overlay module and generated resources.
- `rro/res/xml/vendor.xml` — Generated CarrierConfig XML used by the overlay.

## How It Works

The generator reads Motorola's original CarrierConfig XML from:

`vendor/motorola/rtwo/rro_overlays/CarrierConfigOverlay/res/xml/vendor.xml`

It then processes all XML files inside the `carriers/` directory.

For each carrier configuration, the script:

1. Finds the matching Motorola carrier entry using MCC and MNC.
2. Merges the carrier-specific settings into that entry.
3. Replaces existing values when the same configuration key is defined.
4. Preserves all unrelated Motorola settings.
5. Generates the resulting `vendor.xml` under `rro/res/xml/`.

If a matching carrier entry does not exist, the generator appends a new entry.

## Adding a New Carrier

Adding a carrier does not require modifying the generator.

1. Create a new XML file inside `carriers/`.
2. Name the file using the following convention:

   `MCC_MNC_carrier_name.xml`

3. Add a `carrier_config` element containing the carrier's MCC, MNC, and desired configuration keys.

Example:

`432_11_mci.xml`

```xml
<carrier_config mcc="432" mnc="11">
    <boolean name="carrier_volte_available_bool" value="true" />
</carrier_config>
```

The generator automatically discovers XML files in the `carriers/` directory.

## Generating vendor.xml

Run the following command from the Android source root to regenerate `vendor.xml`:

```bash
python3 device/motorola/rtwo/resource-overlay/device/carrierconfig_ext/gen_carrier_config.py
```

## Validation

To check whether the generated XML is up to date:

```bash
python3 device/motorola/rtwo/resource-overlay/device/carrierconfig_ext/gen_carrier_config.py --check
```

The command exits successfully when the generated file matches the current inputs. Otherwise, it reports that regeneration is required.

After adding or modifying carrier configurations, regenerate the XML and commit the updated output.

## Build Integration

The package is integrated through `device.mk`.

During the Android build, `carrierconfig_ext.mk` runs the generator in check mode. If the generated `vendor.xml` is outdated, the build fails and instructs the developer to regenerate it.

### Why Generation Is Not Automatic

The generator combines inputs from both the device tree and Motorola's vendor tree.

Automatically generating the resource during the build would require additional build-system rules and proper dependency handling for these external inputs.

For now, explicit generation keeps the build integration simple and predictable. The build still validates the generated output to prevent outdated carrier configurations from being included.

## Contributing

Contributions adding support for additional carriers are welcome.

Please provide the appropriate MCC/MNC values and carrier-specific settings, regenerate `vendor.xml`, and include both the new carrier XML and updated generated output in your changes.
