//! The Python runtime, embedded in the `verity` binary.
//!
//! Compiled programs import `testimony` (and `string_ops`) from these
//! files. The CLI writes them next to the generated Python, ahead of
//! `sys.path`, so `.ity` programs need no install and always get the
//! matching runtime. The same files are published as the Python package
//! `verity-testimony`.

/// Source of `runtime/testimony.py`.
pub const TESTIMONY_PY: &str = include_str!("../runtime/testimony.py");

/// Source of `runtime/string_ops.py`.
pub const STRING_OPS_PY: &str = include_str!("../runtime/string_ops.py");
