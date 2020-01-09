
module adc (
	clock_clk,
	reset_sink_reset_n,
	adc_pll_clock_clk,
	adc_pll_locked_export,
	command_valid,
	command_channel,
	command_startofpacket,
	command_endofpacket,
	command_ready,
	response_valid,
	response_channel,
	response_data,
	response_startofpacket,
	response_endofpacket);	

	input		clock_clk;
	input		reset_sink_reset_n;
	input		adc_pll_clock_clk;
	input		adc_pll_locked_export;
	input		command_valid;
	input	[4:0]	command_channel;
	input		command_startofpacket;
	input		command_endofpacket;
	output		command_ready;
	output		response_valid;
	output	[4:0]	response_channel;
	output	[11:0]	response_data;
	output		response_startofpacket;
	output		response_endofpacket;
endmodule
