module max1000 (clk_in, reset_in, leds, rf, lo_i, lo_q, speaker, rs232_tx, 
rs232_cts, rs232_rx, rs232_rtr, bclk_in, lrclk_in, dout_in, sclk_out,  
band, tx_enable, lcd_data, lcd_e, lcd_rs, quad_a, quad_b, sda, scl, sda_pu, scl_pu,
pps);

  input clk_in;
  input reset_in;
  input rs232_rx;
  input pps;
  output rs232_cts;
  input bclk_in;
  input lrclk_in;
  input dout_in;
  output sclk_out;
  output rf;
  output lo_i;
  output lo_q;
  output speaker;
  output [7:0] leds;
  output rs232_tx;
  output rs232_rtr;
  output [2:0] band;
  output tx_enable;
  inout [3:0]lcd_data;
  output reg lcd_e;
  inout lcd_rs;
  input quad_a;
  input quad_b;
  inout scl;
  inout sda;
  output sda_pu;
  output scl_pu;

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
	 
	wire [11:0] audio_in;
	wire audio_in_stb;
	 
	wire [31:0] pb_bus;
	wire pb_stb;
	wire pb_ack;
	 
    wire [31:0] control_bus;
    reg [31:0] control;
    wire control_ack;
    wire control_stb;
	 
    wire [31:0] capture_bus;
    wire capture_ack;
    wire capture_stb;
	 
	wire [31:0] audio_out;
    wire audio_out_ack;
    wire audio_out_stb;
	 
	wire [31:0] power_bus;
    wire power_ack;
    wire power_stb;
	 
	wire [31:0] pps_count_bus;
    wire pps_count_ack;
    wire pps_count_stb;
	 
	 wire [31:0] adc_bus;
    wire adc_ack;
    wire adc_stb;
	 
	 wire [31:0] lcd_bus;
    wire lcd_ack;
    wire lcd_stb;
	 
	 wire [31:0] i2c_in_bus;
    wire i2c_in_ack;
    wire i2c_in_stb;
	 
	 wire [31:0] i2c_out_bus;
    wire i2c_out_ack;
    wire i2c_out_stb;
	 
	 wire [31:0] position_bus;
    wire position_ack;
    wire position_stb;

	 
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
		  
		  .input_i2c_in(i2c_in_bus),
        .input_i2c_in_stb(i2c_in_stb),
        .input_i2c_in_ack(i2c_in_ack),

        .output_i2c_out_stb(i2c_out_stb),
        .output_i2c_out_ack(i2c_out_ack),
        .output_i2c_out(i2c_out_bus),

        .output_frequency_out(frequency_bus),
        .output_frequency_out_ack(frequency_ack),
        .output_frequency_out_stb(frequency_stb),
		  
        .output_control_out(control_bus),
        .output_control_out_ack(control_ack),
        .output_control_out_stb(control_stb),
		  
		.output_lcd_out(lcd_bus),
        .output_lcd_out_ack(lcd_ack),
        .output_lcd_out_stb(lcd_stb),
		  
		.input_pb_in(pb_bus),
        .input_pb_in_ack(pb_ack),
        .input_pb_in_stb(pb_stb),
		  
		.input_capture_in(capture_bus),
        .input_capture_in_ack(capture_ack),
        .input_capture_in_stb(capture_stb),
		  
		.input_power_in(power_bus),
        .input_power_in_ack(power_ack),
        .input_power_in_stb(power_stb),
		  
		.input_pps_count_in(pps_count_bus),
        .input_pps_count_in_ack(pps_count_ack),
        .input_pps_count_in_stb(pps_count_stb),
		  
		.input_adc_in(adc_bus),
        .input_adc_in_ack(adc_ack),
        .input_adc_in_stb(adc_stb),
		  
		.input_position_in(position_bus),
        .input_position_in_ack(position_ack),
        .input_position_in_stb(position_stb)
		  
        //exception
    );

    //implement registers for frequency and control
	 reg [3:0] lcd_data_out;
	 reg lcd_rs_out;
	 reg lcd_oe = 0;
	 
    always @(posedge clk_50) begin

        if (frequency_stb) begin
            frequency <= frequency_bus;
        end

        if (control_stb) begin
            control <= control_bus;
        end
		  
		  if (lcd_stb) begin
            lcd_data_out <= lcd_bus[3:0];
				lcd_e        <= lcd_bus[8];
				lcd_rs_out   <= lcd_bus[9];
				lcd_oe       <= lcd_bus[10];
        end

    end
	 
	 //lcd outputs reused as push button inputs
	 assign lcd_data   = lcd_oe?lcd_data_out:4'bZ;
	 assign lcd_rs     = lcd_oe?lcd_rs_out:1'bZ;
	 assign pb_bus[3:0] = lcd_data;
	 assign pb_bus[4]   = lcd_rs;

    assign frequency_ack = 1;
	 assign audio_in_ack = 1;
	 assign pb_stb = 1;
    assign control_ack = 1;
	 assign power_stb = 1;
	 assign gain_ack = 1;
	 assign pps_count_stb = 1;
	 assign lcd_ack = 1;
	 assign position_stb = 1;
  
     wire [7:0] serial_out;
     wire serial_out_stb;
     wire serial_out_ack;

     serial_mux  serial_mux_0 (
        .clk(clk_50),
    
        .audio_in(audio_out[17:2]),
        .audio_in_stb(audio_out_stb),
        .audio_in_ack(audio_out_ack),

        .serial_out(serial_out),
        .serial_out_stb(serial_out_stb),
        .serial_out_ack(serial_out_ack),

        .serial_in(debug_tx[7:0]),
        .serial_in_stb(debug_tx_stb),
        .serial_in_ack(debug_tx_ack)
    );

    serial_output #(
        .clock_frequency(50000000),
        .baud_rate(1000000)
    )
    serial_output_0(
        .clk(clk_50),
        .rst(rst),
        .tx(rs232_tx),
		.cts(rs232_cts),
       
        .in1(serial_out),
        .in1_stb(serial_out_stb),
        .in1_ack(serial_out_ack)
    );

    wire [7:0] serial_in;
    wire serial_in_stb;
    wire serial_in_ack;

    serial_demux serial_demux_0(
        .clk(clk_50),

        .serial_in(serial_in),
        .serial_in_stb(serial_in_stb),
        .serial_in_ack(serial_in_ack),

        .serial_out(debug_rx[7:0]),
        .serial_out_stb(debug_rx_stb),
        .serial_out_ack(debug_rx_ack),

        .audio_out(audio_in),
        .audio_out_stb(audio_in_stb)
    );

    serial_input #(
        .clock_frequency(50000000),
        .baud_rate(1000000)
    )
    serial_input_0(
        .clk(clk_50),
        .rst(rst),
        .rx(rs232_rx),
		.rtr(rs232_rtr),
       
        .out1(serial_in),
        .out1_stb(serial_in_stb),
        .out1_ack(serial_in_ack)
    );
	 
	 i2c #(
      .CLOCKS_PER_SECOND(50000000),
      .SPEED(100000)
    )
	 i2c_0(
      .clk(clk_50),
      .rst(rst),
 
      .sda(sda),
      .scl(scl),

      .I2C_IN(i2c_out_bus),
      .I2C_IN_STB(i2c_out_stb),
      .I2C_IN_ACK(i2c_out_ack),
 
      .I2C_OUT(i2c_in_bus),
      .I2C_OUT_STB(i2c_in_stb),
      .I2C_OUT_ACK(i2c_in_ack)
    );
    assign sda_pu=1;
	 assign scl_pu=1;
	 
	 rotary_encoder(clk_50, quad_a, quad_b, position_bus);

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
  .pps_in(pps),
  
  //Transceiver Control
  .control_in(control),
  .frequency_in(frequency), 
  .power_out(power_bus),
  
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
  //.leds(leds),
  
  //CPU capture interface
  .capture_out(capture_bus),
  .capture_stb_out(capture_stb),
  
  //CPU capture interface
  .audio_out_out(audio_out),
  .audio_out_stb_out(audio_out_stb),
  .audio_in_in(audio_in),
  .audio_in_stb_in(audio_in_stb),
  
  //GPS 1PPS counter interface
  .pps_count_out(pps_count_bus),
  
  //GPS Route spare ADC channels to CPU
  .adc_out(adc_bus),
  .adc_stb_out(adc_stb),
  
  //band
  .band(band),
  .tx_enable(tx_enable),
  
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
  
  //assign tx_enable = internal_tx_enable?1'b0:1'bZ;

  //use double data rate buffers for rf signals
  
  output_buffer output_buffer_0(
		clk,           
		{rf_1, rf_0}, 
      rf
  );
  output_buffer output_buffer_2(
		clk,           
		{lo_i_1, lo_i_0}, 
      lo_i
  );
  output_buffer output_buffer_3(
		clk,           
		{lo_q_1, lo_q_0}, 
      lo_q
  );
  output_buffer output_buffer_4(
		clk,           
		{test_1, test_0}, 
      test
  );
  
  assign leds[0] = rs232_rtr;
  assign leds[1] = control[25];
  assign leds[2] = control[26];
  assign leds[3] = control[27];
  //assign leds[4] = control[9];
  //assign leds[5] = control[10];
  //assign leds[6] = control[11];
  //assign leds[7] = control[12];
  
  

endmodule
