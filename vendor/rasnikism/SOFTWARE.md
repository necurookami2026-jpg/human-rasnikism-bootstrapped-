# Rasniki kerot software kit

Version 0.1 · A first implemented, expandable collection

“Max” expresses the goal of expanding useful software; it does not mean every software category is implemented. “Ainsuitable” is provisionally interpreted as conformity to the documented K0 instruction contract, not an independently certified property.

## Implemented software

| Component | Status and scope |
| --- | --- |
| Kerot assembler | Two passes, forward labels, six primitive mnemonics, eight-byte instructions, range and syntax validation. |
| K0 interpreter | 64 KiB memory, sixteen registers, bounded execution, byte I/O, declared stop port, explicit faults and input pause. |
| General kerot examples | Console greeting and one-byte echo. |
| Makkakah example | Primitive program emits a sustaining-care message. It demonstrates the toolchain, not autonomous care management. |
| Aantonymmakkakah example | Primitive program emits a reframing-for-repair message. It does not automatically resolve grievances. |
| Existing collection | Static lore archive, configurable reader, and provisional jurisdiction-review tool. |

The host implementation is Python 3 using its standard library. Example target programs use only the six K0 primitives. This is not a toolchain made without existing software, a native CPU language implementation, a bootable Magrigal OS, or a secure sandbox. It is AI-assisted.

## Use

From the repository root:

```sh
python3 software/kerot.py run software/examples/general.kerot
python3 software/kerot.py run software/examples/makkakah.kerot
python3 software/kerot.py run software/examples/aantonymmakkakah.kerot
python3 software/kerot.py run software/examples/echo.kerot --input X
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s software -v
```

Assemble to a new file, then run it:

```sh
python3 software/kerot.py assemble software/examples/general.kerot /tmp/general.k0
python3 software/kerot.py run /tmp/general.k0 --binary --budget 10000
```

The assembler refuses to overwrite an existing output file. Choose a new path for another build. The interpreter writes program output to stdout and execution status to stderr. Exit statuses are 0 for halted, 1 for fault or tool error, 2 for exhausted input, and 3 for exhausted instruction budget.

## Language

One instruction per line. Comments begin with a semicolon. Labels name byte addresses. Registers are r0 through r15; numbers use decimal or Python-style hexadecimal such as 0x41. Commas between arguments are optional.

```text
start: mark r0 65
signal r0 0 1 ; output A
signal r0 2 1 ; stop through the declared device
```

| Form | Action |
| --- | --- |
| mark rN value | Set a register to a 16-bit value. |
| read rN address | Read a byte from memory. |
| write rN address | Write a register's low byte. |
| choose rN zero_label nonzero_label | Branch according to whether the register is zero. |
| step label | Jump. |
| signal rN port direction | Exchange a value with a declared device. |

Port 0 permits output (direction 1), port 1 permits input (direction 0), and port 2 permits stopping (direction 1). Console values are bytes; encode text as UTF-8 bytes when constructing programs. No disk or network port is supplied. Programs can modify their own memory but cannot obtain direct host filesystem or process access through a device.

## Validation and limits

The suite exercises fixed binary encoding, label resolution, reads and writes, both conditional branches, output, stopping, input pause and resume, budget exhaustion, invalid opcodes and fields, instruction-address bounds, rejected source, and all four examples. It does not prove every possible program correct or replace an independent conformance audit.

Memory begins at zero, so executing past a program encounters an invalid opcode unless the program deliberately wrote more instructions. Invalid next addresses fault before the current instruction's side effects. A stopping instruction completes without advancing the PC. Input exhaustion leaves the PC and destination register unchanged. A Python API caller may append input and run again.

The byte output buffer grows with emitted output. Budget execution according to available resources; an instruction limit is not a complete host resource or security boundary.

## Expansion roadmap

Next useful additions are assembly listings, trace inspection, derived routines, a documented record format, and a text-document reader. Makkakah and aantonymmakkakah workflows could later manage records with explicit user decisions. Native boot adapters, memory protection, multitasking, and networking remain separate projects with their own acceptance checks. The earlier architecture documents remain proposals except for this explicitly implemented K0 host toolchain.
