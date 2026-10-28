clc;
clear;
close; close;

N = 32;
l = 7;
Sm = -48;
Sp = 50;
S = 8;
A = 6;

fc = 0.2;
n = 0 : N-1;

h_ideal = sin(2 * %pi * fc * (n - (N-1)/2)) ./ (%pi * (n - (N-1)/2) + %eps);
h_ideal((N-1)/2 + 1) = 2 * fc;

w = 0.42 - 0.5 * cos(2*%pi*n/(N-1)) + 0.08 * cos(4*%pi*n/(N-1));

h = h_ideal .* w;

[H, fr] = frmag(h, 512);

figure(1, 'BackgroundColor', [1,1,1]);

subplot(2, 1, 1);
plot(n, h, 'b.-');
title('Імпульсна характеристика КІХ-фільтра h(n) (Вар. 21)');
xlabel('n');
ylabel('h(n)');
xgrid();

subplot(2, 1, 2);
plot(fr, 20*log10(abs(H) + %eps), 'r-');
title('Амплітудно-частотна характеристика (АЧХ) в дБ');
xlabel('Нормована частота (f/fs)');
ylabel('|H(f)| [дБ]');
xgrid();

max_gain = max(20*log10(abs(H) + %eps));
min_stop = min(20*log10(abs(H) + %eps));

mprintf("\n--- Результати діагностики цифрового фільтра (Варіант 21) ---\n");
mprintf("Порядок фільтра N: %d\n", N);
mprintf("Максимальне посилення в смузі пропускання: %.2f dB\n", max_gain);
mprintf("Рівень згасання в смузі затримування: %.2f dB\n", min_stop);