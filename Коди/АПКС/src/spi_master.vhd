library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spi_master is
    generic (
        DATA_WIDTH : integer := 8;
        CLK_DIV    : integer := 4
    );
    port (
        clk      : in  std_logic;
        reset    : in  std_logic;
        start    : in  std_logic;
        tx_data  : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        rx_data  : out std_logic_vector(DATA_WIDTH-1 downto 0);
        busy     : out std_logic;
        sck      : out std_logic;
        mosi     : out std_logic;
        miso     : in  std_logic;
        ss       : out std_logic
    );
end entity spi_master;

architecture Behavioral of spi_master is
    type state_type is (IDLE, TRANSFER, FINISH);
    signal state : state_type := IDLE;
    
    signal clk_cnt  : integer range 0 to CLK_DIV - 1 := 0;
    signal sck_reg  : std_logic := '0';
    signal bit_cnt  : integer range 0 to DATA_WIDTH := 0;
    
    signal tx_reg   : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');
    signal rx_reg   : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');
begin

    sck <= sck_reg;

    process(clk, reset)
    begin
        if reset = '1' then
            state   <= IDLE;
            busy    <= '0';
            ss      <= '1';
            sck_reg <= '0';
            mosi    <= '0';
            rx_data <= (others => '0');
            clk_cnt <= 0;
            bit_cnt <= 0;
        elsif rising_edge(clk) then
            case state is
                when IDLE =>
                    busy    <= '0';
                    ss      <= '1';
                    sck_reg <= '0';
                    mosi    <= '0';
                    clk_cnt <= 0;
                    bit_cnt <= 0;
                    
                    if start = '1' then
                        state   <= TRANSFER;
                        busy    <= '1';
                        ss      <= '0';
                        tx_reg  <= tx_data;
                        mosi    <= tx_data(DATA_WIDTH-1);
                    end if;

                when TRANSFER =>
                    if clk_cnt = CLK_DIV - 1 then
                        clk_cnt <= 0;
                        if sck_reg = '0' then
                            sck_reg <= '1';
                            rx_reg(DATA_WIDTH - 1 - bit_cnt) <= miso;
                        else
                            sck_reg <= '0';
                            if bit_cnt = DATA_WIDTH - 1 then
                                state <= FINISH;
                            else
                                bit_cnt <= bit_cnt + 1;
                                mosi    <= tx_reg(DATA_WIDTH - 2 - bit_cnt);
                            end if;
                        end if;
                    else
                        clk_cnt <= clk_cnt + 1;
                    end if;

                when FINISH =>
                    sck_reg <= '0';
                    ss      <= '1';
                    busy    <= '0';
                    rx_data <= rx_reg;
                    state   <= IDLE;
            end case;
        end if;
    end process;

end architecture Behavioral;