`timescale 1ns/1ps
module tb_dup;
  reg clk = 0, rst_n = 0, valid_in = 0;
  reg signed [15:0] ar, ai, br, bi, wr, wi;
  reg [15:0] vin [0:32*6-1];
  always #10 clk = ~clk;

  wire signed [15:0] xr [0:8], xi [0:8], yr [0:8], yi [0:8];
  wire vo [0:8], er [0:8];
  genvar g;
  generate for (g = 0; g < 9; g = g + 1) begin : S
    localparam integer BITS = (g==1||g==5) ? 0 : (g==2||g==6) ? 3 : (g==3||g==7) ? 7 : 15;
    butterfly_dup #(.F1(g>=5 ? 1 : 0), .F2(g>=1 ? 1 : 0), .FB(BITS), .FV(1)) d(clk, rst_n, valid_in, ar, ai, br, bi, wr, wi, xr[g], xi[g], yr[g], yi[g], vo[g], er[g]);
  end endgenerate

  integer i, k;
  integer det [0:8];
  initial begin
    $readmemh("vec_in.mem", vin);
    for (k = 0; k < 9; k = k + 1) det[k] = 0;
    #45 rst_n = 1;
    for (i = 0; i < 36; i = i + 1) begin
      @(negedge clk);
      if (i < 32) begin valid_in = 1; ar = vin[i*6]; ai = vin[i*6+1]; br = vin[i*6+2]; bi = vin[i*6+3]; wr = vin[i*6+4]; wi = vin[i*6+5]; end
      else valid_in = 0;
    end
    for (k = 0; k < 9; k = k + 1) $display("СЦЕНАРІЙ %0d: тактів з прапорцем помилки = %0d", k, det[k]);
    $finish;
  end
  always @(posedge clk) for (k = 0; k < 9; k = k + 1) if (er[k]) det[k] = det[k] + 1;
endmodule