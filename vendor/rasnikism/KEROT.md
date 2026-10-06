# Ainsuitable kerot primitive: Magrigal specification

Status: version 0.1, proposed architecture. This document formalizes a fictional vocabulary into an engineering design. It does not supply an implemented operating system, boot image, compiler, or browser. The accompanying archive is implemented in HTML and JavaScript. This publication is AI-assisted.

## Scope and meaning

Kerot names the foundational machine operations. Ainsuitable names conformity to this specification. Rawful names direct construction with recorded derivations. Magrigal names the proposed operating system. These meanings are provisional rather than claims about an established language or tradition.

The intended scope runs from a boot entry point to an interactive document browser. Until the author specifies otherwise, “kerot primitive only” means that the eventual target software has no third-party software dependencies. Existing development tools and hardware are declared hosts, not kerot-derived components. A ban on all existing development tools would require a different bootstrap plan.

## Conformance boundary

Every target component must declare its input and output, memory ownership, permitted device access, dependencies, failure behavior, and derivation to primitives. Undeclared firmware, runtime, libraries, or services invalidate a claim of complete kerot derivation. Hardware and firmware assumptions must remain visible even when target software is self-contained.

Three distinct claims are permitted:

1. **Specified:** a component has a documented contract.
2. **Implemented:** its source and reproducible construction are available.
3. **Verified:** named checks exercise that implementation on a declared host.

The boot, OS, and browser designs remain specified only. The static lore archive is implemented separately. The software kit now supplies a Python-hosted K0 assembler and interpreter with primitive example programs; see SOFTWARE.md.

## Abstract machine K0

K0 has 65,536 addressable unsigned 8-bit marks, an unsigned 16-bit program counter, sixteen unsigned 16-bit registers, an execution status, and declared device ports. Initial RAM and registers are zero except for loaded program bytes and the specified entry point. It uses little-endian encoding. It has no implicit filesystem, network connection, or host-language evaluation.

Each instruction occupies eight bytes: one opcode, one selector, and three little-endian 16-bit fields A, B, C. Unused fields must be zero. The selector contains a register index for instructions that use a register and zero otherwise. A decoder rejects nonzero reserved fields, invalid register selectors, and unsupported opcodes. Instruction fetches must fit completely in memory.

| Opcode | Primitive | Operation |
| --- | --- | --- |
| 0x01 | mark | Set register selector to immediate A; B and C are zero. |
| 0x02 | read | Load memory byte at A into register selector, zero-extended; B and C are zero. |
| 0x03 | write | Store the low eight bits of register selector at memory address A; B and C are zero. |
| 0x04 | choose | If register selector is zero, next PC is A; otherwise next PC is B. C is zero. |
| 0x05 | step | Jump to A; selector, B, and C are zero. |
| 0x06 | signal | Exchange register selector with device port A using direction B: 0 reads, 1 writes. C is zero. |

For mark, read, write, and signal, execution advances PC by eight after successful completion. Overflow faults; PC does not wrap. Branch destinations may be any address at which an entire instruction fits. An unsupported instruction faults before changing state. A device port may explicitly stop execution; K0 has no hidden halt opcode.

Signal operations are atomic from the machine's perspective. Unknown ports and invalid directions fault. Devices declare deterministic behavior or record external input events. Input exhaustion pauses execution without advancing PC or changing the destination register. A host must impose an instruction budget and return a distinguishable budget-exhausted result.

K0 has direct addresses and no native arithmetic or indirect addressing. Finite calculations can be expressed through explicit branch tables, and write can modify program bytes. This deliberately small model may be impractical for large programs. Efficient indexing and arithmetic require either documented derived routines or a reviewed revision of K0; they must not silently become extra primitives.

## Boot chain

The abstract boot path loads a checked program into K0 memory and begins at its declared entry address. This is a simulator contract, not a PC BIOS boot contract.

For legacy x86 BIOS, the disk boot sector is 512 bytes and ends with bytes 0x55, 0xAA. A conventional partitioned master boot record reserves bytes 446–509 for four partition entries, leaving 446 bytes before that table. BIOS transfers control in an x86 real-mode environment, conventionally with the sector at physical address 0x7C00. The entry adapter must establish its own segment registers and stack, preserve the boot-drive identifier, load later stages, check reads, and report failure. The sector alone does not provide K0 execution; an x86 implementation or interpreter of K0 is required.

A UEFI path is separate: a firmware-loadable EFI executable obtains the memory map and necessary boot resources, then follows the UEFI boot-services handoff rules. An MBR signature does not create an EFI executable. Each architecture adapter must disclose its firmware dependencies and device assumptions.

No instruction in this specification authorizes writing an image to a physical disk. Development boot checks should use disposable image files and an emulator.

## Magrigal operating system

The proposed kernel provides these contracts in order:

1. **Memory:** reserve kernel and device regions; track allocation ownership; reject overlapping allocations and out-of-range accesses.
2. **Execution:** maintain task state; initially use cooperative scheduling with explicit yield points and bounded runnable queues.
3. **Devices:** expose typed requests and results; separate console, clock, block storage, and network adapters.
4. **Storage:** use versioned records, length checks, integrity checks, and an explicit recovery procedure for interrupted writes.
5. **Processes:** validate user requests before device or memory operations; provide a defined exit and fault path.
6. **Documents:** expose byte streams with declared encoding and size limits.

K0 alone has no privilege levels or memory isolation. A cooperative runtime can enforce conventions but cannot safely contain arbitrary code with unrestricted write and signal operations. A secure process boundary requires validated restricted programs or a separately specified protected machine. Magrigal must not claim such isolation before it exists.

## Language and construction tools

The first assembler should map primitive mnemonics, register selectors, numeric literals, and labels to K0's eight-byte encoding. It must reject unresolved labels, duplicate labels, invalid fields, and out-of-range values. Assembly listings should show source locations and emitted bytes.

Derived operations must document the primitive sequences they expand into. A bootstrap manifest must list each host tool, version, source input, output, and integrity digest. A future self-hosted assembler must be compared against independently produced reference outputs before replacing its bootstrap tool.

## Browser progression

The first browser target is an offline text-document reader. Its document grammar is UTF-8 plain text with explicit headings and local links; input is bounded and malformed encoding receives a defined error. It must render content, follow valid local links within an allowed root, retain navigation history, and display recoverable errors.

Later milestones may add layout, images, and a documented HTML subset. Full HTML, CSS, JavaScript, HTTPS, certificates, and contemporary web compatibility are separate projects. A restricted reader must describe its supported format and never imply full web-browser compatibility.

Networking requires documented packet drivers, protocol handling, DNS, time, and certificate verification. Unsupported schemes are rejected. Remote content must not obtain unrestricted memory or device access. Script execution remains disabled until an execution boundary is specified and verified.

## Rasniki and ashram integration

The lore archive supplies initial documents for the reader: kerot roots, recursive lore, composition examples, curriculum, shared records, and steading provisions. Each dictionary entry should evolve toward a record containing a stable identifier, root, definition, example, revision, and provenance.

An ashram record is a voluntary organizational artifact, not a grant of legal authority. Names, marks, and stamps never establish ownership of people. Local changes should retain prior versions and attribution. Empire steading denotes revisable cooperation among independent steadings within this fictional framework.

## Acceptance gates

| Milestone | Evidence required |
| --- | --- |
| K0 interpreter | Decode every opcode; check both branch outcomes, byte storage, input pause, device faults, fetch bounds, invalid fields, and budget exhaustion. |
| Assembler | Known encoding fixtures, forward labels, range errors, duplicate labels, and matching reference output. |
| Boot adapter | Disposable image boots in a declared emulator, visibly reaches the entry program, and reports failed reads. |
| Kernel | Allocation ownership, cooperative task progress, malformed requests, storage recovery, and explicit unsupported isolation claims. |
| Document reader | Expected document text, link navigation and history, malformed UTF-8, root escape rejection, and bounded input. |
| Networking | Valid and invalid certificate paths, protocol errors, unavailable hosts, time assumptions, and isolation of remote input. |

The software kit implements and tests the K0 host interpreter and a basic assembler; its documented tests are a first validation, not completion of every acceptance gate above. Boot adapters, a kernel, a document reader, and networking remain unimplemented. HTML archive checks do not substitute for those gates.

## Next construction

K0 and its decoder, a basic assembler, and console examples are now available in the software kit. Next add assembly listings and independent reference checks, then work toward an architecture-specific boot adapter. Keep Python host dependencies explicit and revisit the primitive definition with the author before claiming complete conformance.
