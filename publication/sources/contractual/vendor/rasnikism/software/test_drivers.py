import unittest
from drivers import PortBus
from kerot import Machine, assemble
from pathlib import Path


class DriverTests(unittest.TestCase):
    def test_driver_program(self):
        bus = PortBus(['queue', 'latch', 'clock', 'eventlog'])
        source = (Path(__file__).parent / 'examples/drivers.kerot').read_text()
        machine = Machine(assemble(source), ports=bus)
        self.assertEqual(machine.run(), 'halted')
        self.assertEqual(machine.output, b'A')
        self.assertEqual(bus.devices[17]['value'], 65)
        self.assertEqual(bus.devices[19]['events'], [5])

    def test_wait_detach_and_directions(self):
        bus = PortBus(['queue'])
        machine = Machine(assemble('signal r0 16 0\nsignal r0 0 1\nsignal r0 2 1'), ports=bus)
        self.assertEqual(machine.run(), 'waiting')
        self.assertEqual((machine.pc, machine.steps, machine.registers[0]), (0, 0, 0))
        bus.transfer(16, 1, 81, 0)
        self.assertEqual(machine.run(), 'halted')
        self.assertEqual(machine.output, b'Q')
        bus.detach('queue')
        machine = Machine(assemble('signal r0 16 0'), ports=bus)
        self.assertEqual(machine.run(), 'fault')
        for name, port, direction in [('clock', 18, 1), ('eventlog', 19, 0)]:
            machine = Machine(assemble(f'signal r0 {port} {direction}'), ports=PortBus([name]))
            self.assertEqual(machine.run(), 'fault')

    def test_capacity_and_atomicity(self):
        for name, port, field in [('queue', 16, 'queue'), ('eventlog', 19, 'events')]:
            bus = PortBus([name])
            for _ in range(1024):
                bus.transfer(port, 1, 7, 0)
            machine = Machine(assemble(f'signal r0 {port} 1'), ports=bus)
            self.assertEqual(machine.run(), 'fault')
            self.assertEqual(machine.steps, 0)
            self.assertEqual(len(bus.devices[port][field]), 1024)
        bus = PortBus(['latch'])
        machine = Machine(b'', ports=bus, entry=65528)
        machine.memory[65528:] = assemble('signal r0 17 1')
        machine.registers[0] = 9
        self.assertEqual(machine.run(), 'fault')
        self.assertEqual(bus.devices[17]['value'], 0)
        with self.assertRaises(ValueError):
            bus.attach('latch')
        with self.assertRaises(ValueError):
            bus.attach('unknown')


if __name__ == '__main__':
    unittest.main()
