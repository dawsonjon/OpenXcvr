// adc_modular_adc_0.v

// This file was auto-generated from altera_modular_adc_hw.tcl.  If you edit it your changes
// will probably be lost.
// 
// Generated using ACDS version 19.1 670

`timescale 1 ps / 1 ps
module adc_modular_adc_0 (
		input  wire        clock_clk,              //          clock.clk
		input  wire        reset_sink_reset_n,     //     reset_sink.reset_n
		input  wire        adc_pll_clock_clk,      //  adc_pll_clock.clk
		input  wire        adc_pll_locked_export,  // adc_pll_locked.export
		input  wire        command_valid,          //        command.valid
		input  wire [4:0]  command_channel,        //               .channel
		input  wire        command_startofpacket,  //               .startofpacket
		input  wire        command_endofpacket,    //               .endofpacket
		output wire        command_ready,          //               .ready
		output wire        response_valid,         //       response.valid
		output wire [4:0]  response_channel,       //               .channel
		output wire [11:0] response_data,          //               .data
		output wire        response_startofpacket, //               .startofpacket
		output wire        response_endofpacket    //               .endofpacket
	);

	altera_modular_adc_control #(
		.clkdiv                          (2),
		.tsclkdiv                        (1),
		.tsclksel                        (1),
		.hard_pwd                        (0),
		.prescalar                       (0),
		.refsel                          (1),
		.device_partname_fivechar_prefix ("10M08"),
		.is_this_first_or_second_adc     (1),
		.analog_input_pin_mask           (146),
		.dual_adc_mode                   (0),
		.enable_usr_sim                  (0),
		.reference_voltage_sim           (65536),
		.simfilename_ch0                 (""),
		.simfilename_ch1                 (""),
		.simfilename_ch2                 (""),
		.simfilename_ch3                 (""),
		.simfilename_ch4                 (""),
		.simfilename_ch5                 (""),
		.simfilename_ch6                 (""),
		.simfilename_ch7                 (""),
		.simfilename_ch8                 (""),
		.simfilename_ch9                 (""),
		.simfilename_ch10                (""),
		.simfilename_ch11                (""),
		.simfilename_ch12                (""),
		.simfilename_ch13                (""),
		.simfilename_ch14                (""),
		.simfilename_ch15                (""),
		.simfilename_ch16                ("")
	) control_internal (
		.clk               (clock_clk),              //         clock.clk
		.cmd_valid         (command_valid),          //       command.valid
		.cmd_channel       (command_channel),        //              .channel
		.cmd_sop           (command_startofpacket),  //              .startofpacket
		.cmd_eop           (command_endofpacket),    //              .endofpacket
		.cmd_ready         (command_ready),          //              .ready
		.rst_n             (reset_sink_reset_n),     //    reset_sink.reset_n
		.rsp_valid         (response_valid),         //      response.valid
		.rsp_channel       (response_channel),       //              .channel
		.rsp_data          (response_data),          //              .data
		.rsp_sop           (response_startofpacket), //              .startofpacket
		.rsp_eop           (response_endofpacket),   //              .endofpacket
		.clk_in_pll_c0     (adc_pll_clock_clk),      // adc_pll_clock.clk
		.clk_in_pll_locked (adc_pll_locked_export),  //   conduit_end.export
		.sync_valid        (),                       //   (terminated)
		.sync_ready        (1'b0)                    //   (terminated)
	);

endmodule
