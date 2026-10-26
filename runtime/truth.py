"""The ``truth`` type and its testimony (Verity's Python runtime).

This file is embedded in the Rust ``verity`` binary and written next to
compiled programs. ``truth`` has exactly two constructors, ``verity`` and
``falsity``. A verity carries a *witness* and a falsity carries a
*refutation*; together these are its testimony. This module will provide:

* the ``Truth`` class, usable in Python ``if``/``while``/``all()`` via
  ``__bool__``,
* testimony nodes (comparisons, conjunction/disjunction, negation,
  quantifier witnesses and counterexamples, ``because`` annotations),
* combinators the compiler targets in place of ``and``/``or``/``not``,
  comparisons, ``forall``/``exists`` and ``because``,
* lifting of plain Python bools into truths, and ``to_bool`` for the
  other direction,
* rendering testimony as the indented text shown by ``testimony.explain``.
"""
