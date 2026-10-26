//! The `verity` command-line tool.
//!
//! Planned commands: `verity run file.ity` (compile, write the runtime
//! next to the output, execute with `python3`) and `verity compile
//! file.ity` (print the generated Python). Nothing is implemented yet;
//! see milestone 2 in CLAUDE.md.

/// Runs the CLI with the given arguments and returns the process exit code.
pub fn run(_args: Vec<String>) -> i32 {
    eprintln!("verity: not implemented yet (see milestone 2 in CLAUDE.md)");
    1
}
