set_global_assignment -entity "output_buffer" -library "lib_output_buffer" -name IP_TOOL_NAME "altera_gpio_lite"
set_global_assignment -entity "output_buffer" -library "lib_output_buffer" -name IP_TOOL_VERSION "19.1"
set_global_assignment -entity "output_buffer" -library "lib_output_buffer" -name IP_TOOL_ENV "mwpim"
set_global_assignment -library "lib_output_buffer" -name SPD_FILE [file join $::quartus(sip_path) "output_buffer.spd"]

set_global_assignment -library "lib_output_buffer" -name MISC_FILE [file join $::quartus(sip_path) "output_buffer_sim/output_buffer.v"]
set_global_assignment -library "lib_output_buffer" -name MISC_FILE [file join $::quartus(sip_path) "output_buffer_sim/altera_gpio_lite/altera_gpio_lite.sv"]
