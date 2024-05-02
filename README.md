# Scopy...

Building Gateware:

```bash
mkdir test
python scopy.py --build --load
```

Building Software

```bash
cd firmware
python demo.py --with-cxx --build-path ~/code/verilog/migen/myscope/build/sipeed_tang_primer_20k/software
```

starting litex term
```bash
litex_term /dev/ttyUSB1 --kernel=firmware/demo.bin
```
make sure to be in the root dir!!
