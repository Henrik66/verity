# verity-testimony

Truth values that explain themselves. This is the runtime of the [Verity](https://www.verity.garden) language, packaged so plain Python code and test suites can use it without `.ity` files.

```python
from testimony import all_of, check, explain, reason

def valid_signup(name, age):
    return all_of(
        check(len(name), ">=", 3, src="len(name) >= 3").because(reason("name.length", f"{name!r} has at least 3 characters")),
        check(age, ">=", 13, src="age >= 13").because(reason("age.minimum", "the user is at least 13", hint="ask a parent to sign up")),
    )

print(explain(valid_signup("al", 12)))
```

```
falsity
  failed 2 of 2:
    refuted: 'al' has at least 3 characters [name.length]
      len(name) >= 3: 2 < 3
    refuted: the user is at least 13 [age.minimum]
      hint: ask a parent to sign up
      age >= 13: 12 < 13
```

`to_json(t)` returns the same testimony as JSON (schema `verity.testimony/0`) for tools and agents. The full API is in the [Standard Library](https://www.verity.garden/book/stdlib.html) chapter of *Verity Programming*.

Run the tests from the repository root with `python3 -m unittest discover runtime/tests`.
