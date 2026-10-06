"""Explicitly attached simulated K0 devices; no host hardware or network access."""
CATALOGUE = {'queue': 16, 'latch': 17, 'clock': 18, 'eventlog': 19}


class PortBus:
    def __init__(self, names=()):
        self.devices = {}
        for name in names:
            self.attach(name)

    def attach(self, name):
        if name not in CATALOGUE:
            raise ValueError('Unknown driver: ' + name)
        port = CATALOGUE[name]
        if port in self.devices:
            raise ValueError('Driver already attached')
        self.devices[port] = {'name': name, 'queue': [], 'value': 0, 'events': []}

    def detach(self, name):
        if name not in CATALOGUE or CATALOGUE[name] not in self.devices:
            raise ValueError('Driver not attached')
        del self.devices[CATALOGUE[name]]

    def accepts(self, port, direction):
        return port in self.devices and direction in (0, 1) and not (
            (port == 18 and direction != 0) or (port == 19 and direction != 1))

    def transfer(self, port, direction, value, steps):
        if not self.accepts(port, direction):
            raise ValueError('Unsupported attached port or direction')
        device = self.devices[port]
        if port == 16:
            if direction == 0:
                return None if not device['queue'] else device['queue'].pop(0)
            if len(device['queue']) >= 1024:
                raise ValueError('Queue driver capacity reached')
            device['queue'].append(value & 255)
        elif port == 17:
            if direction == 0:
                return device['value']
            device['value'] = value
        elif port == 18:
            return steps & 65535
        else:
            if len(device['events']) >= 1024:
                raise ValueError('Event driver capacity reached')
            device['events'].append(value)
        return value
