fn main() {
    std::process::exit(verity::cli::run(std::env::args().skip(1).collect()));
}
