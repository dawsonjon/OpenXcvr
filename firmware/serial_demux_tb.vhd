library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity serial_demux_tb is
end entity serial_demux_tb;

architecture rtl of serial_demux_tb is

  signal clk : std_logic;

  signal serial_in : std_logic_vector(7 downto 0);
  signal serial_in_stb : std_logic;
  signal serial_in_ack : std_logic;

  signal serial_out : std_logic_vector(7 downto 0);
  signal serial_out_stb : std_logic;
  signal serial_out_ack : std_logic;

  signal audio_out : std_logic_vector(11 downto 0);
  signal audio_out_stb : std_logic;

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

    send_serial(X"AA"); --audio
    wait for 1 us;
    wait until rising_edge(clk);
    for i in 0 to 1023 loop
      send_serial(X"01");
    end loop;

    send_serial(X"55"); --data
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"01");
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"11");
    wait for 1 us;
    wait until rising_edge(clk);

    send_serial(X"55"); --data
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"02");
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"22");
    wait for 1 us;
    wait until rising_edge(clk);
    send_serial(X"33");
    wait for 1 us;
    wait until rising_edge(clk);



    send_serial(X"AA"); --audio
    for i in 0 to 1023 loop
      send_serial(X"ff");
    end loop;



    wait until rising_edge(clk);

    wait;
  end process;

  dut : entity work.serial_demux port map(
      clk => clk,

      serial_in => serial_in,
      serial_in_stb => serial_in_stb,
      serial_in_ack => serial_in_ack,

      serial_out => serial_out,
      serial_out_stb => serial_out_stb,
      serial_out_ack => serial_out_ack,

      audio_out => audio_out,
      audio_out_stb => audio_out_stb
  );


  serial_out_ack <= '1';


end architecture rtl;
