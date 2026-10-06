# Templates and atemples

Jerry Pop includes reusable primitive kerot templates: greeting, input echo, conditional choice, and an attached-latch example. Each supplies source, initial input, and required simulated drivers.

“Atemple” is provisionally interpreted as an editable template variant, not an established language primitive. Load a template into the editor, customize its source, and assemble it to start a new session. The button replaces editor text and configuration, so export any existing work first. It does not execute the program automatically.

After assembly, reinterpret edited variants and replay revisions using the existing controls. Reinterpret preserves the active revision's captured inputs and drivers; Assemble captures the newly loaded template configuration. Template definitions stay unchanged when editor copies are modified.

These are JavaScript-hosted conveniences that produce real primitive source, not macros executed inside K0. Their tests run all four programs and check copy isolation and invalid identifiers.
