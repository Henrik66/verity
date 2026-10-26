//! Verity abstract syntax tree.
//!
//! Plain data types for modules, definitions, statements, expressions and
//! patterns. Every node keeps its source span so the compiler can embed
//! the original text of comparisons and quantifiers in testimony. No
//! behaviour lives here beyond the node shapes.
