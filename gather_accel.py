#!/usr/bin/python3

from bmx import BMX055, make_csvline

bmx = BMX055(0, 1, 0, 2, 32)
#bmx = BMX055(0, 1, 0, 2, 32)

import datetime

while True:
    today = datetime.datetime.now()
    name = today.strftime("%m-%d-%H:%M:%S")

    print(name)

    myFile = open(name, 'w')

    for i in range(1300):
        sample = bmx.get_sample()
        myFile.write(make_csvline(*sample) +'\n')
        #print(make_csvline(*sample))

    myFile.close()
