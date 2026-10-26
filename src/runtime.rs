//! The Python runtime, embedded in the `verity` binary.
//!
//! Compiled programs import `truth`/testimony support from this file. The
//! CLI writes it next to the generated Python, so users never install a
//! separate Python package.

/// Source of `runtime/truth.py`.
pub const TRUTH_PY: &str = include_str!("../runtime/truth.py");
