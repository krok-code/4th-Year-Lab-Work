`timescale 1ns/1ps
module tb_butterfly;
`ifdef FAULT_INJECT
  localparam FE = 1; localparam FBIT = `FAULT_BIT;
  `ifdef FAULT_VAL0
  localparam FVAL = 0;
  `else
  localparam FVAL = 1;
  `endif
`else
  localparam FE = 0; localparam FBIT = 0; localparam FVAL = 1;
`endif
  reg clk = 0, rst_n = 0, valid_in = 0;
  reg signed [15:0] ar, ai, br, bi, wr, wi;
  wire signed [15:0] xr, xi, yr, yi;
  wire valid_out;
  reg [15:0] vin [0:32*6-1];
  reg [15:0] vex [0:32*4-1];

  butterfly #(.FAULT_EN(FE), .FB(FBIT), .FV(FVAL)) dut(clk, rst_n, valid_in, ar, ai, br, bi, wr, wi, xr, xi, yr, yi, valid_out);
  always #10 clk = ~clk;

  integer i, oc, errors, cyc, t_in, t_out, tf, d, maxerr;
  reg signed [15:0] e0, e1, e2, e3;

  always @(posedge clk) cyc <= cyc + 1;

  initial begin
    $dumpfile("bf.vcd"); $dumpvars(0, tb_butterfly);
    $readmemh("vec_in.mem", vin); $readmemh("vec_exp.mem", vex);
    cyc = 0; oc = 0; errors = 0; maxerr = 0; t_in = -1; t_out = -1;
    tf = $fopen("trace.csv", "w");
    ar = 0; ai = 0; br = 0; bi = 0; wr = 0; wi = 0;
    #45 rst_n = 1;
    for (i = 0; i < 32 + 4; i = i + 1) begin
      @(negedge clk);
      if (i < 32) begin
        valid_in = 1;
        ar = vin[i*6]; ai = vin[i*6+1]; br = vin[i*6+2]; bi = vin[i*6+3]; wr = vin[i*6+4]; wi = vin[i*6+5];
        if (t_in < 0) t_in = cyc;
      end else valid_in = 0;
    end
    $fclose(tf);
    if (errors == 0) $display("Перевірено 32 вектори, помилок: 0\nТЕСТ ПРОЙДЕНО");
    else $display("Перевірено 32 вектори, помилок: %0d [несправність виявлено]", errors);
    $display("Латентність від valid_in до valid_out: %0d тактів", t_out - t_in);
    $display("Максимальна похибка виходу xr: %0d", maxerr);
    $finish;
  end

  always @(posedge clk) if (rst_n) begin
    $fdisplay(tf, "%0d,%b,%b,%0d", cyc, valid_in, valid_out, xr);
    if (valid_out) begin
      if (t_out < 0) t_out = cyc;
      e0 = vex[oc*4]; e1 = vex[oc*4+1]; e2 = vex[oc*4+2]; e3 = vex[oc*4+3];
      if (xr !== e0 || xi !== e1 || yr !== e2 || yi !== e3) begin
        errors = errors + 1;
      end
      d = xr - e0; if (d < 0) d = -d; if (d > maxerr) maxerr = d;
      oc = oc + 1;
    end
  end
endmodule