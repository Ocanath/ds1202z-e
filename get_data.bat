@echo off
python read_ds1202.py 10.0.4.104 -o tmp.npz
python label_channels.py tmp.npz -d

set /p FILENAME="Enter filename (without .npz): "
ren tmp.npz %FILENAME%.npz
echo File saved as %FILENAME%.npz
