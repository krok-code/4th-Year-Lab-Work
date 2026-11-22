module butterfly_dup #(parameter F1 = 0, parameter F2 = 0, parameter FB = 0, parameter FV = 1) (
  input  wire clk, rst_n, valid_in,
  input  wire signed [15:0] ar, ai, br, bi, wr, wi,
  output wire signed [15:0] xr, xi, yr, yi,
  output wire valid_out, err
);
  wire signed [15:0] xr2, xi2, yr2, yi2;
  wire v2;
  butterfly #(.FAULT_EN(F1), .FB(FB), .FV(FV)) u1(clk, rst_n, valid_in, ar, ai, br, bi, wr, wi, xr, xi, yr, yi, valid_out);
  butterfly #(.FAULT_EN(F2), .FB(FB), .FV(FV)) u2(clk, rst_n, valid_in, ar, ai, br, bi, wr, wi, xr2, xi2, yr2, yi2, v2);
  assign err = valid_out & ((xr != xr2) | (xi != xi2) | (yr != yr2) | (yi != yi2));
endmodule