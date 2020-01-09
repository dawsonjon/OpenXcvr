create_clock -name CLK12M -period 83.333 [get_ports {clk_in}]
#derive PLL clocks
derive_pll_clocks
#derive clock uncertainty
derive_clock_uncertainty