# include from device.mk:  $(call inherit-product, device/motorola/rtwo/resource-overlay/device/carrierconfig_ext/carrierconfig_ext.mk)
CC_EXT_DIR := $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST))))

# fail the build if vendor.xml (Motorola) or carriers/*.xml changed and output wasn't regenerated
ifneq ($(shell python3 $(CC_EXT_DIR)/gen_carrier_config.py --check >/dev/null 2>&1; echo $$?),0)
$(error carrierconfig_ext: rro/res/xml/vendor.xml is stale. Run: python3 $(CC_EXT_DIR)/gen_carrier_config.py)
endif

PRODUCT_PACKAGES += CarrierConfigOverlayExt
