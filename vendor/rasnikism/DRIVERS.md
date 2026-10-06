# Jerry Pop: interpretable app, software, ports, and attachables

Jerry Pop is an executable browser app: it assembles primitive K0 source and interprets its bytecode locally. The Python interpreter remains runnable software with matching simulated port drivers. “Comprehensive” means a documented extension framework and current device register, not universal hardware support. This is AI-assisted.

## Implemented ports

| Port | Driver | Directions | Behavior |
| --- | --- | --- | --- |
| 0 | Core console | Write | Emit a byte. |
| 1 | Core input | Read | Consume an input byte or pause without advancing. |
| 2 | Core stop | Write | Halt the machine. |
| 16 | Optional queue | Read/write | Write a low byte; read the oldest byte; empty reads pause. |
| 17 | Optional latch | Read/write | Store or read an unsigned 16-bit value. |
| 18 | Optional clock | Read | Return completed instruction count modulo 65,536; not wall time. |
| 19 | Optional event log | Write | Record an unsigned 16-bit event value. |

Queue and event-log capacities are 1024 entries. A capacity error faults before changing the device. Unknown ports, unsupported directions, and detached drivers fault. Core ports cannot be overridden by the attachment framework. Drivers start empty or zero on attachment; detachment discards their simulated state.

Archangel attachment management means explicit host-selected permissions and visible device state. It grants no supernatural capability. Drivers implement bounded local device behavior and do not open host files, command a shell, connect networks, or control physical devices.

## App execution

Open jerry-pop.html. Choose a quilt example, attach optional drivers, assemble, and click Step or Run. Each run executes at most 1000 instructions. Waiting input can be appended. Changing source or attachments invalidates the old machine and requires reassembly. Output and state are displayed as text, not evaluated as code. Download assembled bytecode if needed.

Browser source uses ASCII labels. Programs and memory are limited to 64 KiB, source to one million characters, cumulative input to 65,536 bytes, and output to 65,536 bytes. The Python interpreter has its previously documented host limits; the browser's additional input/output caps are host resource policy. Neither implementation is a formally audited hostile-code sandbox.

The app loads actual primitive quilt source and interprets it. It does not just display precomputed example results. JavaScript is the declared browser host, while Python is the separate software host; neither host is itself kerot-derived.

## Python software execution

```sh
python3 software/kerot.py run software/examples/drivers.kerot --attach queue --attach latch --attach clock --attach eventlog
```

The demonstration writes and reads queue/latch values and records a clock event. It prints A. The same source can run in Jerry Pop with all four drivers checked. No driver is implicitly enabled in Python.

Programmatic hosts can attach or detach the named drivers through PortBus. The browser UI changes attachments by resetting the machine so running programs cannot silently retain access to a previous configuration. A multiplayer, server, or hardware host requires additional independent work.

## Not implemented

USB, serial, Bluetooth, HID, cameras, microphones, audio synthesis, displays, GPUs, printers, storage devices, network interfaces, GPIO, native kernel drivers, and external game-engine plug-ins are not supplied. They need a selected platform, device protocol, permissions, and platform-specific tests. A simulated port is not a driver for those devices.

## Validation

Run the Python suite and `node software/test_jerry_pop.cjs`. Checks cover real quilt execution and exact bytecode agreement with Python, attached device behavior, empty input, detach faults, invalid directions, capacities, and app controls. They do not certify native hardware compatibility or professional safety.
