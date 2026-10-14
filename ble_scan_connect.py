# ble_scan_connect.py:
from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner, DefaultDelegate
from binascii import hexlify


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)


class NotifyDelegate(DefaultDelegate):
    # Constructor (run once on startup)
    def __init__(self, params):
        DefaultDelegate.__init__(self)

    # func is called on notifications
    def handleNotification(self, cHandle, data):
        print("Notification from Handle: 0x" + format(cHandle, '02X'))
        print(hexlify(data))


scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(1.0)
# print(devices)
n = 0
addr = []
for dev in devices:
    print("%d: Device %s (%s), RSSI=%d dB" % (n, dev.addr, dev.addrType, dev.rssi))
    addr.append([dev.addr, dev.addrType])
    n += 1
    for (adtype, desc, value) in dev.getScanData():
        print(" %s = %s" % (desc, value))
# for item in addr:
#     print(item)
number = input('Enter your device number: ')
print('Device', number)
num = int(number)
print(addr[num][0])
#
print("Connecting...")
dev = Peripheral(addr[num][0], addr[num][1])
dev.withDelegate(NotifyDelegate(dev))
#
print("Services...")
for svc in dev.services:
    print(str(svc))
#
try:
    testService = dev.getServiceByUUID(UUID(0x180D))
    for ch in testService.getCharacteristics():
        print(str(ch))
    #
    ch = dev.getCharacteristics(uuid=UUID(0x2A37))[0]
    ch_handle = ch.getHandle()

    for descriptor in dev.getDescriptors(ch_handle, testService.hndEnd):
        if descriptor.uuid == 0x2902:
            print(f'Client Characteristic Configuration found at handle 0x{format(descriptor.handle, "02X")}')
            cccd_handle = descriptor.handle

    dev.writeCharacteristic(cccd_handle, bytes([2, 0]))
    #
    while True:
        if dev.waitForNotifications(1.0):
            continue
        print("Waiting... Waited more than one sec for notification")
finally:
    dev.disconnect()