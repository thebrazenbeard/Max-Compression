# MaxCompression (MCX)

**A lossless compression library and command-line tool written in C99.**

[![CI](https://github.com/thebrazenbeard/Max-Compression/actions/workflows/ci.yml/badge.svg)](https://github.com/thebrazenbeard/Max-Compression/actions/workflows/ci.yml)
[![GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

MaxCompression offers several compression methods behind one `.mcx` file format and a small C API. Use the command-line tool to compress, restore, inspect, and benchmark files, or link the library into another application. It is designed to explore the trade-off between compression ratio, encoding time, and decoding cost; **the best level depends on the workload**.

This is a reusable software project, not a service that requires a particular host, device, network, or cloud account.

## What it provides

- **Lossless file operations:** `compress`, `decompress`, `verify`, `info`, `cat`, `pipe`, and `bench`, with multi-file and recursive CLI options.
- **Multiple compression paths:** LZ77, Burrows–Wheeler Transform (BWT) with entropy coding, adaptive range-coded LZRC, and a slower context-mixing mode. Level 20 selects a strategy based on input; levels 24/26 expose LZRC and level 28 exposes context mixing.
- **An embeddable C library:** in-memory `mcx_compress()` / `mcx_decompress()`, frame inspection, streaming interfaces, and error helpers in [`include/maxcomp/maxcomp.h`](include/maxcomp/maxcomp.h).
- **Additional integrations:** [Python ctypes bindings](bindings/python/README.md), a [Rust binding crate](bindings/rust/), and [WebAssembly build material](wasm/). Review the applicable binding's build and distribution requirements before use.
- **Testing and benchmarking tools:** CTest-based roundtrip, malformed-input, edge, fuzz-style, streaming, and CLI checks, with a separate benchmark harness.

The current CMake project identifies itself as version **2.2.0**. The compression frame format is described in [the format documentation](docs/FORMAT.md); do not assume arbitrary `.mcx` files can be read by unrelated compression programs.

## Build and try it

Requirements: **CMake 3.15 or later** and a compiler supporting C99. OpenMP is optional. The repository configures CI builds for Linux, macOS, and Windows.

```sh
git clone https://github.com/thebrazenbeard/Max-Compression.git
cd Max-Compression
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

On typical Linux and macOS builds, the CLI is `./build/bin/mcx`. The executable path may differ for multi-configuration generators such as Visual Studio.

```sh
# Compress a sample document; the original is kept by default.
./build/bin/mcx compress --fast sample.txt

# Restore it to a separately named file.
./build/bin/mcx decompress sample.txt.mcx -o restored.txt

# Inspect the frame and verify decompression/integrity.
./build/bin/mcx info sample.txt.mcx
./build/bin/mcx verify sample.txt.mcx sample.txt

# Compare levels and, where installed, external compressors.
./build/bin/mcx bench --compare sample.txt
```

Run the repository test suite:

```sh
ctest --test-dir build --output-on-failure
```

Some integration tests use optional external corpora. A passing test that skips absent corpus files does not establish performance or roundtrip coverage of that corpus. For command flags and supported levels, consult `mcx --help` or [the manual page](docs/mcx.1).

## Choose a compression level

| Level or option | Implemented family | Typical trade-off |
| --- | --- | --- |
| `--fast` / `-l 3` | LZ77 | Favor encoding speed. |
| `--default` / `-l 6` | LZ77 with entropy coding | Balanced choice for general files. |
| `-l 12` | BWT with entropy coding | Higher ratio on some text and structured data; slower encoding. |
| `--best` / `-l 20` | Automatic strategy selection | Ratio-oriented; more work per input. |
| `-l 24` or `-l 26` | LZRC | Alternative range-coded LZ strategy for binary workloads. |
| `-l 28` | Context mixing | Very slow, experimental ratio-oriented option. |

The CLI default is level **3**; `--default` explicitly selects level **6**. Do not confuse those two settings. Start with a representative file and compare output size, elapsed time, and successful roundtrip on your target hardware.

## Use it as a library

The public header is [`<maxcomp/maxcomp.h>`](include/maxcomp/maxcomp.h). One-shot compression uses:

```c
size_t capacity = mcx_compress_bound(input_size);
/* Allocate capacity bytes for output, then call: */
size_t written = mcx_compress(output, capacity, input, input_size, 6);
if (mcx_is_error(written)) {
    /* Handle mcx_get_error_name(written). */
}
```

For a complete allocation, decompression, and byte-for-byte comparison example, see [`examples/simple.c`](examples/simple.c). `mcx_get_frame_info()` accepts the **output structure pointer first**, followed by the buffer and its length; always check its return value. The header documents important thread-safety restrictions: compression uses internal state and is **not thread-safe**, while decompression is documented as stateless.

Python consumers can use the [binding instructions and examples](bindings/python/README.md). Its ctypes layer requires a compatible compiled native library; importing Python alone does not replace the C build prerequisite.

## Benchmarks: read the workload and methodology

The project maintains [benchmark data](BENCHMARKS.md) and [benchmark reproduction notes](docs/RESULTS.md). For example, its documented March 2026 Silesia comparison reports an MCX level-20 total of 48.6 MB versus 49.2 MB for `xz -6`, with `xz` winning on three of the 12 individual files. These are **repository-reported measurements from a specified machine and older version**, not a guarantee of performance on a new file or hardware platform. Results depend on level, corpus, memory budget, compiler, and baseline settings.

Reproduce your own measurements with the provided CLI:

```sh
./build/bin/mcx bench --all-levels sample.txt
./build/bin/mcx bench --format json sample.txt
```

The `--compare` option uses external compression utilities if available. Verify roundtrips before relying on a configuration for archival storage. CRC-based integrity checks detect some corruption but are **not cryptographic authentication**, tamper protection, or a substitute for independent backups.

## Project map

- [`cli/`](cli/) — command-line interface and file operations.
- [`lib/`](lib/) — implemented compression, entropy, preprocessing, and related code.
- [`include/maxcomp/`](include/maxcomp/) — public C API.
- [`bindings/`](bindings/) — language bindings.
- [`tests/`](tests/) — CTest definitions and test programs.
- [`benchmarks/`](benchmarks/) — benchmarking tools.
- [`docs/API.md`](docs/API.md), [`docs/DESIGN.md`](docs/DESIGN.md), [`docs/FORMAT.md`](docs/FORMAT.md) — reference documentation.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md) — contribution and vulnerability-reporting guidance.

## License

MaxCompression is distributed under the [GNU General Public License, version 3](LICENSE). Review that license and the applicable third-party component notices before distributing derivatives or incorporating it into another product.
