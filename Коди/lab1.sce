clc;
clear;
close;close;close;close;

m = 10; 
N = 2^m;

T1 = 27; dt1 = T1 / N;
t1 = 0:dt1:T1-dt1;

N3 = floor(N / 3);
x1 = 18 * ones(1, N3);
x2 = 0 * ones(1, N3);
x3 = 9 * ones(1, N - 2*N3);
x = [x1 x2 x3];

t21 = -70:70/(N/2):0-70/(N/2);
t22 = 0:35/(N/2):35-35/(N/2);
t2 = [t21 t22];

y21 = (18 / 35) * t21;
y22 = (-71 / 35) * t22 + 71;
y = [y21 y22];

figure(1, 'BackgroundColor', [1, 1, 1]);
plot(t1, x, 'r');
plot(t2, y, 'g');
legend('Вхідний сигнал - x(n)', 'Вхідний сигнал - y(n)');
title('Вхідні сигнали');
xgrid();

Bxx = (1 / N) * xcorr(x, x);
figure(2, 'BackgroundColor', [1, 1, 1]);
plot(Bxx, 'b');
title('Автокореляційна функція сигналу X');
xgrid();

Byy = (1 / N) * xcorr(y, y);
figure(3, 'BackgroundColor', [1, 1, 1]);
plot(Byy, 'b');
title('Автокореляційна функція сигналу Y');
xgrid();

Bxy = (1 / (2 * N)) * xcorr(x, y);
figure(4, 'BackgroundColor', [1, 1, 1]);
plot(Bxy, 'b');
title('Взаємокореляційна функція сигналів X та Y');
xgrid();