import platform
import subprocess


"""
Class retrieves temperature sensor readings from ln-sensors
"""


class TempCheck:

    TEMP_ERR = -274

    def __init__(self):
        self.hostname = platform.node()
        self.logname = "/var/log/sensors.log"

    def run_process(self, exe):
        p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while(True):
            retcode = p.poll()
            line = p.stdout.readline()
            yield line
            if(retcode is not None):
                break

    """
    voidmain@tao12:~$ sensors
    atk0110-acpi-0
    Adapter: ACPI interface
    Vcore Voltage:      +1.10 V  (min =  +0.85 V, max =  +1.60 V)
     +3.3 Voltage:      +3.31 V  (min =  +2.97 V, max =  +3.63 V)
     +5 Voltage:        +5.02 V  (min =  +4.50 V, max =  +5.50 V)
     +12 Voltage:      +12.10 V  (min = +10.20 V, max = +13.80 V)
    CPU FAN Speed:     2789 RPM  (min =  600 RPM, max = 7200 RPM)
    CHASSIS FAN Speed:    0 RPM  (min =  600 RPM, max = 7200 RPM)
    POWER FAN Speed:      0 RPM  (min =  600 RPM, max = 7200 RPM)
    CPU Temperature:    +42.0°C  (high = +60.0°C, crit = +95.0°C)
    MB Temperature:     +31.0°C  (high = +45.0°C, crit = +75.0°C)

    k10temp-pci-00c3
    Adapter: PCI adapter
    temp1:        +41.4°C  (high = +70.0°C)
                           (crit = +99.5°C, hyst = +97.5°C)

    """
    def decode_temp(self, text):

        def temp2str(temp):
            # remove °C
            deg_pos = temp.find("°C")
            if deg_pos >= 0:
                return float(temp[:deg_pos].strip())  # remove °C
            else:  # not degrees... what is going on?
                return self.TEMP_ERR # below absolute zero... is an error

        vals = text.split()

        temp_cur = temp2str(vals[0])

        temp_high = self.TEMP_ERR
        if len(vals) > 3:
            if vals[1] == "(high":
                temp_high = temp2str(vals[3])
        return temp_cur, temp_high

    def get_temp(self):

        temp_sensors = {"CPU": "CPU Temperature:",
                        "MB": "MB Temperature:",
                        "AMB": "temp1:"}
        # note: executing just 'sensors' is not working due to direct output to TTY
        # using 'script' to capture entire output
        out = self.run_process(["script", "-c", "sensors > $(tty)"])
        for l in out:
            lstr = l.decode('utf-8')
            for s in temp_sensors:
                if temp_sensors[s] in lstr:
                    lstr = lstr[len(temp_sensors[s]):]
                    temp_cur, temp_high = self.decode_temp(lstr)
                    print(s, temp_cur, temp_high)


def main():
    pass

if __name__ == "__main__":
    main()
