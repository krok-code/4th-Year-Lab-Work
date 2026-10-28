clc;
clear;
close; close;

T = 27; 
N = 256;
p = N / 4;

dt = T / N;
t = 0 : dt : T - dt;
t = t(1:N);

N3 = floor(N / 3);
x1 = 18 * ones(1, N3);
x2 = 0 * ones(1, N3);
x3 = 9 * ones(1, N - 2*N3);
x = [x1 x2 x3];

w = 1:N;
Sx = fft(x) / N;

figure(1, 'BackgroundColor', [1,1,1]);
subplot(3, 1, 1); plot(t, x); title('Вхідний сигнал - x(n)'); xgrid();
subplot(3, 1, 2); plot(w, real(Sx)); title('Дійсна частина ШПФ'); xgrid();
subplot(3, 1, 3); plot(w, imag(Sx)); title('Уявна частина ШПФ'); xgrid();

k1 = N/2 - p;
k2 = N/2 + p;

Sx1 = Sx;
Sx1(k1+1 : k2) = 0;

Sx2 = zeros(1, N);
Sx2(p+1 : N-p) = Sx(p+1 : N-p);

Sx3 = Sx;
Sx3(N/4 - p/2 + 1 : N/4 + p/2) = 0;
Sx3(3*N/4 - p/2 + 1 : 3*N/4 + p/2) = 0;

Sx4 = zeros(1, N);
Sx4(N/4 - p/2 + 1 : N/4 + p/2) = Sx(N/4 - p/2 + 1 : N/4 + p/2);
Sx4(3*N/4 - p/2 + 1 : 3*N/4 + p/2) = Sx(3*N/4 - p/2 + 1 : 3*N/4 + p/2);

x1_rec = real(N * ifft(Sx));
xm1    = real(N * ifft(Sx1));
xm2    = real(N * ifft(Sx2));
xm3    = real(N * ifft(Sx3));
xm4    = real(N * ifft(Sx4));

figure(2, 'BackgroundColor', [1,1,1]);

subplot(5, 2, 1); plot(w, abs(Sx));  title('Амплітудний спектр X(k)'); xgrid();
subplot(5, 2, 3); plot(w, abs(Sx1)); title('Модифікований спектр Xm1(k)'); xgrid();
subplot(5, 2, 5); plot(w, abs(Sx2)); title('Модифікований спектр Xm2(k)'); xgrid();
subplot(5, 2, 7); plot(w, abs(Sx3)); title('Модифікований спектр Xm3(k)'); xgrid();
subplot(5, 2, 9); plot(w, abs(Sx4)); title('Модифікований спектр Xm4(k)'); xgrid();

subplot(5, 2, 2);  plot(t, x1_rec); title('Відновлений сигнал x1(n)'); xgrid();
subplot(5, 2, 4);  plot(t, xm1);    title('Відновлений сигнал xm1(n)'); xgrid();
subplot(5, 2, 6);  plot(t, xm2);    title('Відновлений сигнал xm2(n)'); xgrid();
subplot(5, 2, 8);  plot(t, xm3);    title('Відновлений сигнал xm3(n)'); xgrid();
subplot(5, 2, 10); plot(t, xm4);    title('Відновлений сигнал xm4(n)'); xgrid();

onePr = 100 / (N * max(abs(x)));
bm1 = onePr * sum(abs(x - xm1));
bm2 = onePr * sum(abs(x - xm2));
bm3 = onePr * sum(abs(x - xm3));
bm4 = onePr * sum(abs(x - xm4));

mprintf("\nN = %d\n", N);
mprintf("p = %d\n", p);
mprintf("bm1 = %.4f %%\n", bm1);
mprintf("bm2 = %.4f %%\n", bm2);
mprintf("bm3 = %.4f %%\n", bm3);
mprintf("bm4 = %.4f %%\n", bm4);
