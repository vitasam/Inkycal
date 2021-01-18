import arrow
from inkycal import Inkycal

now = arrow.now()
start = now.format('DD-MM-YYYY HH:mm:ss')
print(f'Inkycal starting. Date and time: {start}\n')

print('--------------loading settings file------------')
inky = Inkycal('/home/pi/settings.json', render = True)
print('--------------settings file loaded-------------')

print('--------------testing inkycal------------------')
inky.test()
print('--------------test complete--------------------')

print('--------------starting main program------------')
inky.run()
