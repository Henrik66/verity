//! Verity: a quirky functional Python where booleans testify.
//!
//! The pipeline is `.ity` source → [`lexer`] → [`parser`] → [`ast`] →
//! [`compiler`] → Python source. Compiled programs import the small Python
//! runtime embedded by [`runtime`].

pub mod ast;
pub mod cli;
pub mod compiler;
pub mod lexer;
pub mod parser;
pub mod runtime;
