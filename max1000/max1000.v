module max1000 (clk_in, reset_in, leds, rf, lo_i, lo_q, audio_out, rs232_tx, rs232_rx);

  input clk_in;
  input reset_in;
  input rs232_rx;
  output rf;
  output lo_i;
  output lo_q;
  output audio_out;
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

  //adc interface
  //
  wire [11:0] tx_audio;
  wire tx_audio_stb;

  adc_test u_adc_test(
      .adc_clk(clk_10), 
      .clk(clk), 
      .response_channel(response_channel), 
      .response_data(response_data), 
      .response_valid(response_valid),
      .command_ready(command_ready), 
      .command_channel(command_channel), 
      .command_startofpacket(command_startofpacket), 
      .command_endofpacket(command_endofpacket),
	   .tx_audio(tx_audio),
	   .tx_audio_stb(tx_audio_stb)
  );

  assign leds[7:1] = response_data[11:4];
  assign leds[0] = response_valid;
  

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
        .output_control_out_stb(control_stb)
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
  //add rf
  wire [7:0] audio_i;
  wire [7:0] audio_q;

  wire rf_0;
  wire rf_1;
  wire lo_i_0;
  wire lo_i_1;
  wire lo_q_0;
  wire lo_q_1;

  transceiver tx_0(clk, frequency, tx_audio[11:4], tx_audio_stb, control[1:0], control[2], rf_0, rf_1, lo_i_0, lo_i_1, lo_q_0, lo_q_1);
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
