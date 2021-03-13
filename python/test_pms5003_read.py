import pms5003

p = pms5003.PMS5003()

p.gather(num=31)

print(p.buffer)

p.uart.close()
