#[test]
fn runtime_is_embedded() {
    assert!(verity::runtime::TRUTH_PY.contains("truth"));
}
