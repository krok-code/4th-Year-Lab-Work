clc;
clear;
close; close;

fs = 20000;
T = 0.1;
dt = 1 / fs;
t = 0 : dt : T - dt;
N = length(t);

f1 = 4556;
f2 = 5113;
s = sin(2*%pi*f1*t) + 0.5*sin(2*%pi*f2*t);

f_noise = 5730;
noise = 0.3 * sin(2*%pi*f_noise*t) + 0.1 * rand(1, N, "normal");
x = s + noise;

a = 0.95;
x_pre = zeros(1, N);
x_pre(1) = x(1);
for n = 2:N
    x_pre(n) = x(n) - a * x(n-1);
end

fc = 5000;
alpha = exp(-2 * %pi * fc / fs);
x_filt = zeros(1, N);
x_filt(1) = x_pre(1);
for n = 2:N
    x_filt(n) = (1 - alpha) * x_pre(n) + alpha * x_filt(n-1);
end

figure(1, 'BackgroundColor', [1,1,1]);

subplot(3, 1, 1);
plot(t(1:300), x(1:300));
title('Зашумлений мовний сигнал x(n) (Вар. 21)');
xgrid();

subplot(3, 1, 2);
plot(t(1:300), x_pre(1:300));
title('Сигнал після Pre-emphasis');
xgrid();

subplot(3, 1, 3);
plot(t(1:300), x_filt(1:300));
title('Сигнал після НЧ-фільтрації');
xgrid();

f = (0 : N/2 - 1) * (fs / N);
S_x = abs(fft(x)) / N;
S_x = S_x(1:N/2);

S_pre = abs(fft(x_pre)) / N;
S_pre = S_pre(1:N/2);

S_filt = abs(fft(x_filt)) / N;
S_filt = S_filt(1:N/2);

figure(2, 'BackgroundColor', [1,1,1]);

subplot(3, 1, 1);
plot(f, S_x);
title('Спектр вхідного сигналу (4556, 5113, 5730 Гц)');
xgrid();

subplot(3, 1, 2);
plot(f, S_pre);
title('Спектр після Pre-emphasis');
xgrid();

subplot(3, 1, 3);
plot(f, S_filt);
title('Спектр після НЧ-фільтрації');
xgrid();

energy_orig = sum(x.^2);
energy_filt = sum(x_filt.^2);

mprintf("\n--- Результати для Варіанта 21 ---\n");
mprintf("f1 = %d Hz, f2 = %d Hz, f_noise = %d Hz\n", f1, f2, f_noise);
mprintf("Енергія вхідного сигналу: %.4f\n", energy_orig);
mprintf("Енергія відфільтрованого сигналу: %.4f\n", energy_filt);