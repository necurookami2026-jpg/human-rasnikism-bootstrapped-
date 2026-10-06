"""K0 assembler and bounded reference interpreter; Python is the declared host."""
import argparse
import struct
import sys
from pathlib import Path

SIZE = 65536
OPS = {'mark': 1, 'read': 2, 'write': 3, 'choose': 4, 'step': 5, 'signal': 6}
ARITY = {'mark': 2, 'read': 2, 'write': 2, 'choose': 3, 'step': 1, 'signal': 3}


def assemble(source):
    """Two-pass assembly; labels are byte addresses, comments start with ;."""
    labels, rows, pc = {}, [], 0
    for number, line in enumerate(source.splitlines(), 1):
        line = line.split(';', 1)[0].strip()
        if not line:
            continue
        if ':' in line:
            label, line = line.split(':', 1)
            label = label.strip()
            if not label.isidentifier() or label in labels:
                raise ValueError(f'line {number}: invalid or duplicate label')
            labels[label] = pc
            line = line.strip()
        if not line:
            continue
        parts = line.replace(',', ' ').split()
        op, args = parts[0], parts[1:]
        if op not in OPS or len(args) != ARITY[op]:
            raise ValueError(f'line {number}: unknown instruction or wrong arity')
        rows.append((number, op, args))
        pc += 8
        if pc > SIZE:
            raise ValueError('program exceeds K0 memory')

    def value(token):
        v = labels[token] if token in labels else int(token, 0)
        if not 0 <= v < SIZE:
            raise ValueError('value out of range')
        return v

    output = bytearray()
    for number, op, args in rows:
        try:
            reg = 0
            if op != 'step':
                token = args.pop(0)
                if not token.startswith('r') or not token[1:].isdigit():
                    raise ValueError('register must be r0 through r15')
                reg = int(token[1:])
                if reg > 15:
                    raise ValueError('register out of range')
            fields = [value(t) for t in args]
            if op == 'signal' and fields[1] not in (0, 1):
                raise ValueError('signal direction must be 0 or 1')
            fields += [0] * (3 - len(fields))
            output.extend(struct.pack('<BBHHH', OPS[op], reg, *fields))
        except ValueError as exc:
            raise ValueError(f'line {number}: {exc}') from exc
    return bytes(output)


class Machine:
    """Ports: 0 output byte, 1 input byte, 2 stop (write only)."""
    def __init__(self, program, input_bytes=b'', entry=0, ports=None):
        if len(program) > SIZE or not 0 <= entry <= SIZE - 8:
            raise ValueError('invalid program size or entry point')
        self.memory = bytearray(SIZE)
        self.memory[:len(program)] = program
        self.registers = [0] * 16
        self.pc = entry
        self.input = bytearray(input_bytes)
        self.input_offset = 0
        self.output = bytearray()
        self.status = 'ready'
        self.error = None
        self.steps = 0
        self.ports = ports

    def fault(self, message):
        self.status, self.error = 'fault', message
        return False

    def step(self):
        if self.status in ('halted', 'fault'):
            return False
        if not 0 <= self.pc <= SIZE - 8:
            return self.fault('instruction fetch out of bounds')
        op, reg, a, b, c = struct.unpack_from('<BBHHH', self.memory, self.pc)
        if op not in OPS.values() or reg > 15 or c:
            return self.fault('invalid opcode, selector, or reserved field')
        if (op in (1, 2, 3) and b) or (op == 5 and (reg or b)):
            return self.fault('nonzero reserved field')
        core_port = (a, b) in ((0, 1), (1, 0), (2, 1))
        attached_port = a >= 16 and self.ports is not None and self.ports.accepts(a, b)
        if op == 6 and (b not in (0, 1) or not (core_port or attached_port)):
            return self.fault('unsupported device port or direction')
        next_pc = self.pc + 8
        if op == 4:
            next_pc = a if self.registers[reg] == 0 else b
        elif op == 5:
            next_pc = a
        stopping = op == 6 and a == 2
        if not stopping and not 0 <= next_pc <= SIZE - 8:
            return self.fault('next instruction address out of bounds')
        if op == 6 and a == 1 and self.input_offset == len(self.input):
            self.status = 'waiting'
            return False
        if op == 6 and attached_port:
            try:
                value = self.ports.transfer(a, b, self.registers[reg], self.steps)
            except ValueError as exc:
                return self.fault(str(exc))
            if value is None:
                self.status = 'waiting'
                return False
            if b == 0:
                self.registers[reg] = value
        if op == 1:
            self.registers[reg] = a
        elif op == 2:
            self.registers[reg] = self.memory[a]
        elif op == 3:
            self.memory[a] = self.registers[reg] & 255
        elif op == 6:
            if a == 0:
                self.output.append(self.registers[reg] & 255)
            elif a == 1:
                self.registers[reg] = self.input[self.input_offset]
                self.input_offset += 1
        self.steps += 1
        self.status = 'halted' if stopping else 'ready'
        if not stopping:
            self.pc = next_pc
        return True

    def run(self, budget=10000):
        if budget < 1:
            raise ValueError('budget must be positive')
        if self.status in ('halted', 'fault'):
            return self.status
        for _ in range(budget):
            if not self.step() or self.status == 'halted':
                return self.status
        self.status = 'budget-exhausted'
        return self.status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    asm = commands.add_parser('assemble')
    asm.add_argument('source', type=Path)
    asm.add_argument('output', type=Path)
    run = commands.add_parser('run')
    run.add_argument('source', type=Path)
    run.add_argument('--binary', action='store_true')
    run.add_argument('--input', default='')
    run.add_argument('--budget', type=int, default=10000)
    run.add_argument('--attach', action='append', default=[], choices=['queue', 'latch', 'clock', 'eventlog'])
    args = parser.parse_args()
    try:
        if args.command == 'assemble':
            data = assemble(args.source.read_text())
            with args.output.open('xb') as output:
                output.write(data)
            return 0
        data = args.source.read_bytes() if args.binary else assemble(args.source.read_text())
        ports = None
        if args.attach:
            from drivers import PortBus
            ports = PortBus(args.attach)
        machine = Machine(data, args.input.encode('utf-8'), ports=ports)
        status = machine.run(args.budget)
        sys.stdout.buffer.write(machine.output)
        print(f'\nK0: {status}; {machine.steps} instructions' +
              (f'; {machine.error}' if machine.error else ''), file=sys.stderr)
        return {'halted': 0, 'fault': 1, 'waiting': 2, 'budget-exhausted': 3}[status]
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
