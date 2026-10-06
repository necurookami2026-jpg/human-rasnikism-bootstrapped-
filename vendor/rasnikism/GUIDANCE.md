# Troubleshooting, practical tips, and guidance

This guide describes the implemented Rasniki tools. “Insider tips” means practical implementation knowledge, not confidential information or professional advice.

## Choose the correct entry point

Use Jerry Pop to assemble and execute primitive programs in a browser. Use software/quilt.py to run named quilt modes in Python. Use publication.html to verify and read encoded records; the publication reader does not execute them. Use the catalogue to distinguish implemented utilities from proposed specialist systems.

## Jerry Pop troubleshooting

| Symptom | Meaning | Next step |
| --- | --- | --- |
| Run is disabled | There is no current assembled machine, or source/attachments changed. | Assemble a fresh session or reinterpret edited source in an existing session. |
| Waiting | An input or queue read has no available byte. | Append decimal bytes for core input. For a queue, provide data through its host bus or revise the program so it writes before reading. |
| Budget-exhausted | The machine completed its allowed instruction slice. | Inspect the PC and source for a loop; another Run continues. It is not proof of a fault. |
| Halted | The program wrote to stop port 2. | Replay, reinterpret, or assemble to run from a fresh state. |
| Fault | An instruction, address, port, direction, or capacity check failed. | Read the reported error and state, correct the source or attachments, and create a fresh machine. |
| Unknown instruction / register | The source does not match K0 syntax. | Use mark, read, write, choose, step, signal and registers r0–r15. |
| Unknown port | A port is absent or its direction is unsupported. | Check the port register and attach required simulated drivers before assembly. |
| Queue or event capacity reached | A simulated driver reached 1024 entries. | Redesign consumption or event volume; reassembly resets its state. |

Driver changes never grant physical device access. Clock port 18 reads completed instruction count, not actual elapsed time. Output is interpreted as UTF-8 for display; arbitrary byte output can show replacement characters without indicating a CPU fault.

## Revisions and templates

Loading a template replaces editor text and configuration but does not run it. Assemble captures its inputs and attachments into a new session. Reinterpret uses the active revision's captured initial inputs and drivers, even if the current input field or checkboxes have changed. Use Assemble for a new configuration.

Replay restores source and starts a fresh machine. It does not restore mid-program memory or later feed-button input. Export revisions before reload; the page does not retain them. Histories have bounded retention, so an old revision may no longer be available.

## Kernel-language tips

Labels are byte addresses; each instruction occupies eight bytes. Zero-filled memory beyond a program is not an implicit halt: executing it faults. Finish deliberately with a signal to port 2.

The branch primitive tests zero versus nonzero; it does not compare arbitrary numbers. Byte writes keep the low eight bits. Registers and latch values are 16-bit. The basic machine has no built-in addition, stack, filesystem, or indirect addressing. The quilt's exact addition is a finite branch-based Boolean calculation.

Use small examples first, inspect registers after a step, and test both branch paths. Compare generated source assembly with the published binary when verifying an edition. Never describe an input named consent or permission as verified consent merely because it is nonzero.

## Python tool troubleshooting

Run from the repository root and use Python 3. The assembler refuses to overwrite an output file: choose a new path instead of assuming the build replaced it. Console input supplied by --input is UTF-8 text; the quilt runner supplies actual Boolean bytes for you.

Interpreter exit codes are 0 halted, 1 fault/tool error, 2 missing input, and 3 exhausted instruction budget. Capture stdout and stderr separately: stdout is program output, stderr is execution status. A driver example needs its --attach options; drivers are not enabled automatically.

If the quilt runner reports an integrity mismatch, rebuild with software/build_quilt.py and run the checks. Do not edit the expected digest just to suppress a mismatch.

## Encoded publication troubleshooting

If integrity verification fails, use an intact publication or rebuild from known source. Base64 is not encryption, and included digests do not authenticate an unknown sender. Do not execute imported records merely because their integrity checks pass.

The reader requires Web Crypto. If it is unavailable, try a browser context supporting it; use the documented local HTTP server where appropriate. The reader must not bypass verification. Malformed script instructions, duplicate paths, bad UTF-8, oversized imports, and incorrect byte counts are rejected.

After editing sources, refresh compiled editions and encoded publication data with their build scripts. Stale encoded records show the previous build, not the current editor contents. Preserve the original license.

## Good working order

1. Choose a small, specific task and the implemented tool that supports it.
2. Read its inputs, limits, and required attachments.
3. Save existing work before replacing it.
4. Run a known example, then make one change at a time.
5. Check behavior and failure paths before expanding the task.
6. Export useful records and regenerate publication artifacts after source changes.

Legal, clinical, spiritual, hardware, and emergency-response claims retain their documented limits. Guidance cannot turn a proposed component into an implementation or certify a result beyond its tested scope.
