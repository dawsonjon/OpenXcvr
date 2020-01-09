set_global_assignment -entity "io" -library "lib_io" -name IP_TOOL_NAME "altera_gpio_lite"
set_global_assignment -entity "io" -library "lib_io" -name IP_TOOL_VERSION "19.1"
set_global_assignment -entity "io" -library "lib_io" -name IP_TOOL_ENV "mwpim"
set_global_assignment -library "lib_io" -name SPD_FILE [file join $::quartus(sip_path) "io.spd"]

set_global_assignment -library "lib_io" -name MISC_FILE [file join $::quartus(sip_path) "io_sim/io.v"]
set_global_assignment -library "lib_io" -name MISC_FILE [file join $::quartus(sip_path) "io_sim/altera_gpio_lite/altera_gpio_lite.sv"]
