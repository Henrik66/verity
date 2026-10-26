//! Compile a Verity AST into Python source.
//!
//! * Rewrites `and`/`or`/`not`, comparisons, `forall`/`exists` and
//!   `because` into calls on the Python runtime, since Python cannot
//!   overload the boolean operators. Comparisons whose operands return
//!   non-bool values (numpy arrays, pandas series) must pass through
//!   untouched.
//! * Lowers Coconut-style features (pipes, partial application,
//!   composition, `match`, `data`, `addpattern`) to plain Python.
//! * Runs the testimony-erasure pass: where a `truth` is only used for
//!   control flow and its testimony is never observed, emits plain Python
//!   booleans so ordinary branching costs nothing extra.
