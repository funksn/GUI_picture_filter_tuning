import sys

def read_settings(settings_file):
    f = open(settings_file)
    mic = {}
    for x in f:
        words = x.split()
        if "#" not in words:
            try:
                mic[words[0]] = float(words[2])
            except:
                try:
                    mic[words[0]] = str(words[2])
                except:
                    sys.exit(" > Could not translate settings...")
    f.close()
    mic["minRad"] = int(mic["minRad"])
    mic["maxRad"] = int(mic["maxRad"])
    mic["minDist"] = int(mic["minDist"])
    mic["par1"] = int(mic["par1"])
    mic["par2"] = int(mic["par2"])
    mic["crop_xmin"] = int(mic["crop_xmin"])
    mic["crop_xmax"] = int(mic["crop_xmax"])
    mic["crop_ymin"] = int(mic["crop_ymin"])
    mic["crop_ymax"] = int(mic["crop_ymax"])
    mic["erode"] = int(mic["erode"])
    mic["dilate"] = int(mic["dilate"])
    mic["canny"] = int(mic["canny"])
    mic["nphi"] = int(mic["nphi"])
    mic["fft"] = int(mic["fft"])
    mic["f_cutoff"] = int(mic["f_cutoff"])
    mic["lower_th_canny"] = int(mic["lower_th_canny"])
    mic["upper_th_canny"] = int(mic["lower_th_canny"])
    mic["iteration"] = int(mic["iteration"])
    mic["highpass"] = int(mic["highpass"])
    mic["medfilt"] = int(mic["medfilt"])
    mic["binarize"] = int(mic["binarize"])
    mic["binarize_th"] = int(mic["binarize_th"])
    return mic

def test_read_settings():
    settings_file = './../settings/settings_probst1'
    mic = read_settings(settings_file)
    key = mic.keys()
    val = mic.values()
    print(val)
    for (k, v) in zip(key, val):
        print(k, v, type(v))

if __name__=='__main__':
    test_read_settings()