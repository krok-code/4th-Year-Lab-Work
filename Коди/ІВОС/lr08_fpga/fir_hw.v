module fir_hw #(parameter NTAPS = 147, parameter FAULT_EN = 0, parameter FB = 0) (
  input wire clk,
  input wire signed [15:0] x_in,
  output reg signed [15:0] y
);
  reg signed [15:0] coef [0:NTAPS-1];
  reg signed [15:0] sr [0:NTAPS-1];
  reg signed [47:0] acc;
  integer k;
  initial begin
    $readmemh("fir_coeff.mem", coef);
    for (k = 0; k < NTAPS; k = k + 1) sr[k] = 0;
    y = 0;
  end
  always @(posedge clk) begin
    acc = coef[0] * x_in;
    for (k = 1; k < NTAPS; k = k + 1) acc = acc + coef[k] * sr[k-1];
    for (k = NTAPS-1; k > 0; k = k - 1) sr[k] <= sr[k-1];
    sr[0] <= x_in;
    acc = acc >>> 15;
    if (acc > 48'sd32767) y <= 16'sd32767;
    else if (acc < -48'sd32768) y <= -16'sd32768;
    else y <= (FAULT_EN == 0) ? acc[15:0] : (acc[15:0] | (16'sd1 << FB));
  end
endmodule