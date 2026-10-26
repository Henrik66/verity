//! Hand-written parser: turns tokens into a Verity [`crate::ast`].
//!
//! Recursive descent for statements and definitions, Pratt parsing for
//! expressions so the precedence of `because`, `|>`, `..>`, `$`,
//! comparisons and `and`/`or`/`not` lives in one table. Produces
//! readable errors pointing at the offending source span.
