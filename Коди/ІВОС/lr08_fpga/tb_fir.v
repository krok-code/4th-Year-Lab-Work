`timescale 1ns/1ps
module tb_fir;
  reg clk = 0;
  reg signed [15:0] x = 0;
  wire signed [15:0] y;
  reg [15:0] xs [0:16383];
  integer i, f;
`ifdef FAULT_INJECT
  fir_hw #(.NTAPS(147), .FAULT_EN(1), .FB(`FAULT_BIT)) dut(clk, x, y);
`else
  fir_hw #(.NTAPS(147)) dut(clk, x, y);
`endif
  always #10 clk = ~clk;
  initial begin
    $readmemh("chirp.mem", xs);
    f = $fopen(`OUTF, "w");
    for (i = 0; i < 16384 + 2; i = i + 1) begin
      @(negedge clk);
      x = (i < 16384) ? xs[i] : 16'sd0;
      if (i >= 1) $fdisplay(f, "%0d", y);
    end
    $fclose(f);
    $finish;
  end
endmodule