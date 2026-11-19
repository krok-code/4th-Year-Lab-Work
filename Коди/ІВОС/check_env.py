import sys, shutil

print("Python", sys.version.split()[0])
for m in ["numpy", "scipy", "matplotlib", "pyfda", "soundfile", "PIL"]:
    try:
        __import__(m)
        print(f"  {m:12s} OK")
    except ImportError:
        print(f"  {m:12s} ВІДСУТНІЙ")

for exe in ["octave", "iverilog", "gtkwave", "renode", "arm-none-eabi-gcc", "gnuradio-companion"]:
    print(f"  {exe:20s}", "OK" if shutil.which(exe) else "ВІДСУТНІЙ")