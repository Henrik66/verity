//! Compile a Verity AST into Python source.
//!
//! * Rewrites `and`/`or`/`not`, comparisons, `forall`/`exists` and
//!   `because` into calls on the Python runtime, since Python cannot
//!   overload the boolean operators. Comparisons whose operands return
//!   non-bool values (numpy arrays, pandas series) must pass through
//!   untouched.
//! * Rewrites `assert` to raise `TestimonyError` carrying the falsity.
//! * Dual compilation: each truth-returning function gets an evidence
//!   version and a value version, and calls that are only branched on use
//!   the value version, so ordinary branching costs nothing extra.
