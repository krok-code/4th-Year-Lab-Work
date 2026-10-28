library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_spi_master is
end entity tb_spi_master;

architecture Behavioral of tb_spi_master is
    constant DATA_WIDTH : integer := 8;
    constant CLK_PERIOD : time := 10 ns;

    signal clk     : std_logic := '0';
    signal reset   : std_logic := '1';
    signal start   : std_logic := '0';
    signal tx_data : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');
    signal rx_data : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal busy    : std_logic;
    
    signal sck     : std_logic;
    signal mosi    : std_logic;
    signal miso    : std_logic := '0';
    signal ss      : std_logic;

    signal slave_tx : std_logic_vector(7 downto 0) := "01011010";
    signal bit_idx  : integer range 0 to 7 := 7;
begin

    clk_process : process
    begin
        clk <= '0';
        wait for CLK_PERIOD / 2;
        clk <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    uut: entity work.spi_master
        generic map (
            DATA_WIDTH => DATA_WIDTH,
            CLK_DIV    => 4
        )
        port map (
            clk     => clk,
            reset   => reset,
            start   => start,
            tx_data => tx_data,
            rx_data => rx_data,
            busy    => busy,
            sck     => sck,
            mosi    => mosi,
            miso    => miso,
            ss      => ss
        );

    slave_proc : process(sck, ss)
    begin
        if ss = '1' then
            bit_idx <= 7;
            miso    <= slave_tx(7);
        elsif rising_edge(sck) then
            miso <= slave_tx(bit_idx);
            if bit_idx > 0 then
                bit_idx <= bit_idx - 1;
            end if;
        end if;
    end process;

    stim_proc : process
    begin
        reset <= '1';
        wait for 20 ns;
        reset <= '0';
        wait for 20 ns;

        tx_data <= "10100101";
        start   <= '1';
        wait for CLK_PERIOD;
        start   <= '0';

        wait until busy = '0';
        wait for 100 ns;

        assert false report "Simulation Completed Successfully!" severity failure;
        wait;
    end process;

end architecture Behavioral;