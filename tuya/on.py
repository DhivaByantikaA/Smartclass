import tinytuya

# Connect to Device
# d = tinytuya.OutletDevice(
#     dev_id='eb21a45ab22c089709sf2t',
#     address='192.168.100.9',      # Or set to 'Auto' to auto-discover IP address
#     local_key='D&8bUeO!j}|Pi{lT', 
#     version=3.3)

d = tinytuya.OutletDevice(
    dev_id='eb21a45ab22c089709sf2t',
    address='192.168.100.9',      # Or set to 'Auto' to auto-discover IP address
    local_key='D&8bUeO!j}|Pi{lT', 
    version=3.3)

# Get Status
data = d.status() 
print('set_status() result %r' % data)

# Turn On
# d.set_value(1, True)
# d.turn_on()

# Turn Off
# d.turn_off()