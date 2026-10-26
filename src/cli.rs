//! The `verity` command-line tool.
//!
//! Planned commands: `verity check`, `verity run`, `verity compile` and
//! `verity test`, each with `--json` for machine-readable records (see the
//! Machine Interface chapter of the book). Nothing is implemented yet;
//! see milestone 2 in CLAUDE.md.

/// Runs the CLI with the given arguments and returns the process exit code.
pub fn run(_args: Vec<String>) -> i32 {
    eprintln!("verity: not implemented yet (see milestone 2 in CLAUDE.md)");
    1
}
