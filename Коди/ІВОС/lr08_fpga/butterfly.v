module butterfly #(parameter FAULT_EN = 0, parameter FB = 0, parameter FV = 1) (
  input  wire clk, rst_n, valid_in,
  input  wire signed [15:0] ar, ai, br, bi, wr, wi,
  output reg  signed [15:0] xr, xi, yr, yi,
  output reg  valid_out
);
  reg signed [31:0] p1, p2, p3, p4;
  reg signed [15:0] ar_d, ai_d;
  reg v1;

  wire signed [32:0] dr = {p1[31], p1} - {p2[31], p2};
  wire signed [32:0] di = {p3[31], p3} + {p4[31], p4};
  wire signed [32:0] tr33 = dr >>> 15;
  wire signed [32:0] ti33 = di >>> 15;
  wire signed [17:0] tr = tr33[17:0];
  wire signed [17:0] ti = ti33[17:0];

  wire signed [18:0] sxr = $signed({{3{ar_d[15]}}, ar_d}) + $signed({tr[17], tr});
  wire signed [18:0] sxi = $signed({{3{ai_d[15]}}, ai_d}) + $signed({ti[17], ti});
  wire signed [18:0] syr = $signed({{3{ar_d[15]}}, ar_d}) - $signed({tr[17], tr});
  wire signed [18:0] syi = $signed({{3{ai_d[15]}}, ai_d}) - $signed({ti[17], ti});

  wire signed [15:0] xr_n = (sxr >>> 1);
  wire signed [15:0] xi_n = (sxi >>> 1);
  wire signed [15:0] yr_n = (syr >>> 1);
  wire signed [15:0] yi_n = (syi >>> 1);

  wire signed [15:0] xr_f = (FAULT_EN == 0) ? xr_n : (FV ? (xr_n | (16'sd1 << FB)) : (xr_n & ~(16'sd1 << FB)));

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      p1 <= 0; p2 <= 0; p3 <= 0; p4 <= 0;
      ar_d <= 0; ai_d <= 0; v1 <= 0;
      xr <= 0; xi <= 0; yr <= 0; yi <= 0; valid_out <= 0;
    end else begin
      p1 <= br * wr; p2 <= bi * wi; p3 <= br * wi; p4 <= bi * wr;
      ar_d <= ar; ai_d <= ai; v1 <= valid_in;
      xr <= xr_f; xi <= xi_n; yr <= yr_n; yi <= yi_n; valid_out <= v1;
    end
  end
endmodule