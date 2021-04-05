--serial mux
--allow packets of audio or status info to be transferred over a single audio link.

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity serial_mux_tb is
end entity serial_mux_tb;

architecture rtl of serial_mux_tb is
    signal clk : std_logic;
    
    signal audio_in     : std_logic_vector(15 downto 0);
    signal audio_in_stb : std_logic;
    signal audio_in_ack : std_logic;

    signal serial_out     : std_logic_vector(7 downto 0);
    signal serial_out_stb : std_logic;
    signal serial_out_ack : std_logic;

    signal serial_in     : std_logic_vector(7 downto 0);
    signal serial_in_stb : std_logic;
    signal serial_in_ack : std_logic;

    signal tx : std_logic;
    signal cts : std_logic;


begin

  generate_clock : process
  begin

    loop
      clk <= '0';
      wait for 10 ns;
      clk <= '1';
      wait for 10 ns;
    end loop;
    wait;

  end process;


  process

    procedure send_serial (a : in std_logic_vector) is
    begin
      serial_in <= a;
      serial_in_stb <= '1';
      loop
        wait until rising_edge(clk);
        if serial_in_ack = '1' and serial_in_stb = '1' then
          serial_in_stb <= '0';
          exit;
        end if;
      end loop;
    end procedure;


  begin

    serial_in_stb <= '0';
    wait for 1 us;
    wait until rising_edge(clk);

    --send_serial(X"AA");
    wait for 1 us;
    send_serial(X"00"); --cmd
    wait for 1 us;
    send_serial(X"00"); --cmd
    wait for 1 us;
    send_serial(X"00"); --cmd
    wait for 1 us;
    send_serial(X"55"); --cmd
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"01"); --length
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"33"); --data
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"55"); --cmd
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"01"); --length
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"33"); --data
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"55"); --cmd
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"01"); --length
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"33"); --data
    wait for 1 us;
    wait until rising_edge(clk);

     


    wait;
  end process;




  dut : entity work.serial_mux port map(
    clk  => clk,
    
    audio_in  => audio_in,
    audio_in_stb  => audio_in_stb,
    audio_in_ack  => audio_in_ack,

    serial_out     => serial_out,
    serial_out_stb => serial_out_stb,
    serial_out_ack => serial_out_ack,

    serial_in      => serial_in,
    serial_in_stb  => serial_in_stb,
    serial_in_ack  => serial_in_ack
);


serial_out_1 : entity work.serial_output generic map(
    CLOCK_FREQUENCY => 50000000,
    BAUD_RATE       => 2000000
  )
  port map(
    CLK     => clk,
    RST     => '0',
    TX      => tx,
    CTS     => cts,
   
    IN1     => serial_out,
    IN1_STB => serial_out_stb,
    IN1_ACK => serial_out_ack
  );

audio_in <= X"1234";
audio_in_stb <= '1';
cts <= '0';

end rtl;

