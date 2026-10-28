clc;
clear;
close; close;

N = 256;
[X, Y] = meshgrid(1:N, 1:N);
img = uint8(128 + 127 * sin(X/10) .* cos(Y/10));

img_d = double(img);

block_size = 8;
num_blocks = N / block_size;

Q = [
 16  11  10  16  24  40  51  61;
 12  12  14  19  26  58  60  55;
 14  13  16  24  40  57  69  56;
 14  17  22  29  51  87  80  62;
 18  22  37  56  68 109 103  77;
 24  35  55  64  81 104 113  92;
 49  64  78  87 103 121 120 101;
 72  92  95  98 112 100 103  99
];

scale = 2.0;
Q_scaled = Q * scale;

dct_img = zeros(N, N);
quant_img = zeros(N, N);
rec_img = zeros(N, N);

for i = 1:num_blocks
    for j = 1:num_blocks
        row_range = (i-1)*block_size + 1 : i*block_size;
        col_range = (j-1)*block_size + 1 : j*block_size;
        
        block = img_d(row_range, col_range) - 128;
        
        dct_block = dct(block);
        dct_img(row_range, col_range) = dct_block;
        
        q_block = round(dct_block ./ Q_scaled);
        quant_img(row_range, col_range) = q_block;
        
        idct_block = idct(q_block .* Q_scaled) + 128;
        rec_img(row_range, col_range) = idct_block;
    end
end

rec_img = max(0, min(255, rec_img));

rmse = sqrt(mean((img_d - rec_img).^2));
psnr = 10 * log10((255^2) / (rmse^2));

non_zero_orig = N * N;
zero_count = sum(bool2s(quant_img == 0));
non_zero_quant = N*N - zero_count;
compression_ratio = non_zero_orig / max(1, non_zero_quant);

figure(1, 'BackgroundColor', [1,1,1]);

subplot(1, 2, 1);
grayplot(1:N, 1:N, img_d);
title('Оригінальне зображення');

subplot(1, 2, 2);
grayplot(1:N, 1:N, rec_img);
title('Відновлене зображення після ДКП та квантування');

mprintf("\n--- Результати стиску зображення ---\n");
mprintf("Середньоквадратична похибка (RMSE): %.4f\n", rmse);
mprintf("Пікове співвідношення сигнал/шум (PSNR): %.2f dB\n", psnr);
mprintf("Коефіцієнт стиску: %.2f : 1\n", compression_ratio);
