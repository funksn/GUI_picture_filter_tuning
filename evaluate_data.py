import pandas as pd
import os

manual_data = pd.DataFrame()

for file in os.listdir(r'C:\Users\Stefan\bwSyncAndShare\LehrlaborEnergietechnik (Matthias Probst)\imgs\LaserDuenn_Vol250_pd200\Cam1_001A'):
    if file.split('.') =='csv':
