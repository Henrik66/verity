//! Hand-written lexer: turns `.ity` source text into tokens.
//!
//! Handles Python-style significant indentation by emitting `Indent`,
//! `Dedent` and `Newline` tokens (ignoring newlines inside brackets),
//! and recognises Python's keywords plus Verity's (`verity`, `falsity`,
//! `because`, `forall`, `exists`). Every token carries a
//! source span so testimony can later quote the original expression text.
