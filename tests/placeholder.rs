#[test]
fn runtime_is_embedded() {
    assert!(verity::runtime::TESTIMONY_PY.contains("testimony"));
    assert!(verity::runtime::STRING_OPS_PY.contains("String predicates"));
}
