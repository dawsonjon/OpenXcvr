--serial mux
--allow packets of audio or status info to be transferred over a single audio link.

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity serial_mux is
  port(
    clk : std_logic;
    
    audio_in     : in std_logic_vector(15 downto 0);
    audio_in_stb : in std_logic;
    audio_in_ack : out std_logic;

    serial_out     : out std_logic_vector(7 downto 0);
    serial_out_stb : out std_logic;
    serial_out_ack : in std_logic;

    serial_in     : in std_logic_vector(7 downto 0);
    serial_in_stb : in std_logic;
    serial_in_ack : out std_logic
);
end entity serial_mux;

architecture rtl of serial_mux is

  type state_type is (get_command, put_audio_header, get_audio, put_audio_low, 
    put_audio_high, get_length, put_header, put_length, get_serial, put_serial);
  signal state : state_type := get_command;
  signal audio : std_logic_vector(15 downto 0);
  signal count : integer range 0 to 1023;
  signal data : std_logic_vector(7 downto 0);
  signal s_serial_out_stb : std_logic := '0';

begin

  process
  begin
    wait until rising_edge(clk);

    case state is

      when get_command =>
        if serial_in_stb = '1' then
          if serial_in = X"AA" then
            state <= put_audio_header;
            count <= 1023;
          elsif serial_in = X"55" then
            state <= get_length;
          end if;
        end if;

      --process an audio packet
      when put_audio_header =>
        serial_out <= X"AA";
        s_serial_out_stb <= '1';
        if serial_out_ack = '1' and s_serial_out_stb = '1' then
          s_serial_out_stb <= '0';
          state <= get_audio;
        end if;

      when get_audio =>
        if audio_in_stb = '1' then
          audio <= audio_in;
          state <= put_audio_low;
        end if;

      when put_audio_low =>
        serial_out <= audio(7 downto 0);
        s_serial_out_stb <= '1';
        if serial_out_ack = '1' and s_serial_out_stb = '1' then
          s_serial_out_stb <= '0';
          state <= put_audio_high;
        end if;

      when put_audio_high =>
        serial_out <= audio(15 downto 8);
        s_serial_out_stb <= '1';
        if serial_out_ack = '1' and s_serial_out_stb = '1' then
          s_serial_out_stb <= '0';
          if count = 0 then
            state <= get_command;
          else
            count <= count - 1;
            state <= get_audio;
          end if;
        end if;

      --put a control packet
      when get_length =>
        if serial_in_stb = '1' then
          count <= to_integer(unsigned(serial_in));
          state <= put_header;
        end if;

      when put_header =>
        serial_out <= X"55";
        s_serial_out_stb <= '1';
        if serial_out_ack = '1' and s_serial_out_stb = '1' then
          s_serial_out_stb <= '0';
          state <= put_length;
        end if;

      when put_length =>
        serial_out <= std_logic_vector(to_unsigned(count, 8));
        s_serial_out_stb <= '1';
        if serial_out_ack = '1' and s_serial_out_stb = '1' then
          s_serial_out_stb <= '0';
          count <= count - 1;
          state <= get_serial;
        end if;

      when get_serial =>
        if serial_in_stb = '1' then
          data <= serial_in;
          state <= put_serial;
        end if;
        
      when put_serial =>
        serial_out <= data;
        s_serial_out_stb <= '1';
        if serial_out_ack = '1' and s_serial_out_stb = '1' then
          s_serial_out_stb <= '0';
          if count = 0 then
            state <= get_command;
          else
            state <= get_serial;
            count <= count - 1;
          end if;
        end if;

    end case;
  end process;

  serial_in_ack <= '1' when state = get_command else
                   '1' when state = get_length else
                   '1' when state = get_serial else
                   '0';

  audio_in_ack <= '1' when state = get_audio else '0';

  serial_out_stb <= s_serial_out_stb;

end rtl;

