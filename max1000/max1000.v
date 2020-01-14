module max1000 (clk_in, reset_in, leds, rf, lo_i, lo_q, speaker, rs232_tx, rs232_rx, bclk_in, lrclk_in, dout_in, sclk_out, pps_in);

  input clk_in;
  input reset_in;
  input rs232_rx;
  input bclk_in;
  input lrclk_in;
  input dout_in;
  input pps_in;
  output sclk_out;
  output rf;
  output lo_i;
  output lo_q;
  output speaker;
  output [7:0] leds;
  output rs232_tx;

////////////////////////////////////////////////////////////////////////////////
//RESET AND CLOCKS
//
  wire clk_150;
  wire clk_50;
  wire clk_10;
  wire locked;
  reg locked_d;
  wire clk;
  reg rst;
  wire rst_n;
  xcvr_pll pll_0( areset, clk_in, clk_150, clk_10, clk_50, locked);
  assign clk = clk_150;
  always@(posedge clk_50) begin
    locked_d <= locked;
    rst <= ~locked_d;
  end
  assign rst_n = ~rst;

////////////////////////////////////////////////////////////////////////////////
//MAX10 FPGA builtin ADC
//
  wire command_valid;
  wire [4:0] command_channel;
  wire command_startofpacket;
  wire command_endofpacket;
  wire command_ready;
  wire response_valid;
  wire [4:0] response_channel;
  wire [11:0] response_data;
  wire response_startofpacket;
  wire response_endofpacket;

  adc u0 (
		.clock_clk              (clk_10),
		.reset_sink_reset_n     (rst_n),
		.adc_pll_clock_clk      (clk_10),
		.adc_pll_locked_export  (locked),
		.command_valid          (command_valid),
		.command_channel        (command_channel),
		.command_startofpacket  (command_startofpacket),
		.command_endofpacket    (command_endofpacket),
		.command_ready          (command_ready),
		.response_valid         (response_valid),
		.response_channel       (response_channel),
		.response_data          (response_data),
		.response_startofpacket (response_startofpacket),
		.response_endofpacket   (response_endofpacket)
	);

  assign command_valid = 1;
  assign response_ready = 1;

////////////////////////////////////////////////////////////////////////////////
//Software Control
//

    wire [31:0] debug_rx;
    wire debug_rx_stb;
    wire debug_rx_ack;

    wire [31:0] debug_tx;
    wire debug_tx_stb;
    wire debug_tx_ack;

    wire [31:0] frequency_bus;
    reg [31:0] frequency;
    wire frequency_stb;
    wire frequency_ack;

    wire [31:0] control_bus;
    reg [31:0] control;
    wire control_ack;
    wire control_stb;
	 
    wire [31:0] capture_bus;
    wire capture_ack;
    wire capture_stb;
	 
	 wire [31:0] power_bus;
    wire power_ack;
    wire power_stb;
	 
	 wire [31:0] gain_bus;
    wire gain_ack;
    wire gain_stb;
	 
	 wire [31:0] pps_count_bus;
    wire pps_count_ack;
    wire pps_count_stb;
	 
	 wire [31:0] adc_bus;
    wire adc_ack;
    wire adc_stb;

	 
    //implement compiled C program
    main_0 control_sw_0(
        .clk(clk_50),
        .rst(rst),

        .input_debug_in(debug_rx),
        .input_debug_in_stb(debug_rx_stb),
        .input_debug_in_ack(debug_rx_ack),

        .output_debug_out_stb(debug_tx_stb),
        .output_debug_out_ack(debug_tx_ack),
        .output_debug_out(debug_tx),

        .output_frequency_out(frequency_bus),
        .output_frequency_out_ack(frequency_ack),
        .output_frequency_out_stb(frequency_stb),

        .output_control_out(control_bus),
        .output_control_out_ack(control_ack),
        .output_control_out_stb(control_stb),
		  
		  .input_capture_in(capture_bus),
        .input_capture_in_ack(capture_ack),
        .input_capture_in_stb(capture_stb),
		  
		  .input_power_in(power_bus),
        .input_power_in_ack(power_ack),
        .input_power_in_stb(power_stb),
		  
		  .input_pps_count_in(pps_count_bus),
        .input_pps_count_in_ack(pps_count_ack),
        .input_pps_count_in_stb(pps_count_stb),
		  
		  .output_gain_out(gain_bus[5:0]),
        .output_gain_out_ack(gain_ack),
        .output_gain_out_stb(gain_stb),
		  
		  .input_adc_in(adc_bus),
        .input_adc_in_ack(adc_ack),
        .input_adc_in_stb(adc_stb)
		  
        //exception
    );

    //implement registers for frequency and control
    always @(posedge clk_50) begin

        if (frequency_stb) begin
            frequency <= frequency_bus;
        end

        if (control_stb) begin
            control <= control_bus;
        end

    end

    assign frequency_ack = 1;
    assign control_ack = 1;
	 assign power_stb = 1;
	 assign gain_ack = 1;
	 assign pps_count_stb = 1;

    serial_output #(
        .clock_frequency(50000000),
        .baud_rate(115200)
    )
    serial_output_0(
        .clk(clk_50),
        .rst(rst),
        .tx(rs232_tx),
       
        .in1(debug_tx[7:0]),
        .in1_stb(debug_tx_stb),
        .in1_ack(debug_tx_ack)
    );

    serial_input #(
        .clock_frequency(50000000),
        .baud_rate(115200)
    )
    serial_input_0(
        .clk(clk_50),
        .rst(rst),
        .rx(rs232_rx),
       
        .out1(debug_rx[7:0]),
        .out1_stb(debug_rx_stb),
        .out1_ack(debug_rx_ack)
    );

  ////////////////////////////////////////////////////////////////////////////////
  //Transceiver
  //

  wire rf_0;
  wire rf_1;
  wire lo_i_0;
  wire lo_i_1;
  wire lo_q_0;
  wire lo_q_1;
  
  transceiver transceiver_u0(
  
  .clk(clk), 
  .adc_clk(clk_10),
  .cpu_clk(clk_50),
  
  //GPS 1pps counter input
  .pps_in(pps_in),
  
  //Transceiver Control
  .filter_mode_in(control[1:0]), 
  .filter_sideband_in(control[2]), 
  .rx_tx_in(control[3]),
  .volume_in(control[13:8]),
  .frequency_in(frequency), 
  .power_out(power_bus),
  .gain_in(gain_bus),
  
  //ADC INTERFACE
  .response_channel_in(response_channel), 
  .response_data_in(response_data), 
  .response_valid_in(response_valid), 
  .command_ready_in(command_ready), 
  .command_channel_out(command_channel),
  .command_startofpacket_out(command_startofpacket),
  .command_endofpacket_out(command_endofpacket),
  
  //External ADC interface
  .bclk_in(bclk_in),
  .lrclk_in(lrclk_in),
  .dout_in(dout_in),
  .sclk_out(sclk_out),
  .leds(leds),
  
  //CPU capture interface
  .capture_out(capture_bus),
  .capture_stb_out(capture_stb),
  
  //GPS 1PPS counter interface
  .pps_count_out(pps_count_bus),
  
  //GPS Route spare ADC channels to CPU
  .adc_out(adc_bus),
  .adc_stb_out(adc_stb),
  
  //RF INTERFACE
  .rf_0_out(rf_0), 
  .rf_1_out(rf_1), 
  .lo_i_0_out(lo_i_0), 
  .lo_i_1_out(lo_i_1), 
  .lo_q_0_out(lo_q_0), 
  .lo_q_1_out(lo_q_1),
  
  //AUDIO OUTPUT
  .speaker_out(speaker)
  );

  //use double data rate buffers for rf signals
  
  output_buffer output_buffer_0(
		clk,           
		{rf_1, rf_0}, 
      rf
  );
  output_buffer output_buffer_1(
		clk,           
		{lo_i_1, lo_i_0}, 
      lo_i
  );
  output_buffer output_buffer_2(
		clk,           
		{lo_q_1, lo_q_0}, 
      lo_q
  );

endmodule
