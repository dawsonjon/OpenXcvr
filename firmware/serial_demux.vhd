library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity serial_demux is
  port(
    clk : in std_logic;

    serial_in : in std_logic_vector(7 downto 0);
    serial_in_stb : in std_logic;
    serial_in_ack : out std_logic;

    serial_out : out std_logic_vector(7 downto 0);
    serial_out_stb : out std_logic;
    serial_out_ack : in std_logic;

    audio_out : out std_logic_vector(11 downto 0);
    audio_out_stb : out std_logic := '0'
);
end entity serial_demux;

architecture rtl of serial_demux is

  type state_type is (get_command, audio_get_serial, wait_tick, audio_put,
      get_length, get_data, put_data);

  signal state : state_type := get_command;

  signal s_serial_in_ack : std_logic := '0';
  signal s_serial_out_stb : std_logic := '0';
  signal count : integer range 0 to 1023;
  signal data : std_logic_vector(7 downto 0);
  signal timer : integer range 0 to 999;
  signal tick : std_logic;

begin

  --timer goes every 1000 clocks giving a sample rate of 50KHz for a 50MHz clock
  process
  begin
    wait until rising_edge(clk);
    if timer = 0 then
      tick <= '1';
      timer <= 999;
    else
      tick <= '0';
      timer <= timer - 1;
    end if;
  end process;

  --route audio packets marked "AA" to the transmitter, but send an "AA" marker to the CPU
  --route command packets marked "55" to the CPU
  process
  begin
    wait until rising_edge(clk);

    case state is
      
      when get_command =>
        s_serial_in_ack <= '1';
        if serial_in_stb = '1' and s_serial_in_ack = '1' then
          s_serial_in_ack <= '0';
          if serial_in = X"AA" then
            count <= 1023;
            state <= audio_get_serial;
          elsif serial_in = X"55" then
            state <= get_length;
          end if;
        end if;


      --send an audio packet to the transceiver input
      when audio_get_serial =>
        s_serial_in_ack <= '1';
        if serial_in_stb = '1' and s_serial_in_ack = '1' then
          audio_out <= serial_in & "0000";
          s_serial_in_ack <= '0';
          state <= wait_tick;
        end if;

      when wait_tick =>
        if tick = '1' then
          state <= audio_put;
          audio_out_stb <= '1';
        end if;

      when audio_put =>
        audio_out_stb <= '0';
        if count = 0 then
          state <= get_command;
        else
          state <= audio_get_serial;
          count <= count - 1;
        end if;


      --send a control packet to the CPU
      when get_length =>
        s_serial_in_ack <= '1';
        if serial_in_stb = '1' and s_serial_in_ack = '1' then
          count <= to_integer(unsigned(serial_in))-1;
          s_serial_in_ack <= '0';
          state <= get_data;
        end if;

      when get_data =>
        s_serial_in_ack <= '1';
        if serial_in_stb = '1' and s_serial_in_ack = '1' then
          s_serial_in_ack <= '0';
          data <= serial_in;
          state <= put_data;
        end if;

      when put_data =>
        serial_out <= data;
        s_serial_out_stb <= '1';
        if serial_out_ack = '1' and s_serial_out_stb = '1' then
          s_serial_out_stb <= '0';
          if count = 0 then
            state <= get_command;
          else
            count <= count - 1;
            state <= get_data;
          end if;
        end if;

    end case;

  end process;

  serial_in_ack <= s_serial_in_ack;
  serial_out_stb <= s_serial_out_stb;

end architecture rtl;
