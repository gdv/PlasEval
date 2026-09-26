# Change log

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- The order of keywords:
## [Unreleased] - yyyy-mm-dd

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security
-->

<!-- next-header -->
## [Unreleased] - yyyy-mm-dd

### Added

* Tests under `tests` folder

### Changed

**⚠️ Breaking changes:**

* For all CLI subcommands:
  * `--min_len` to `--min-len`
  * `--log_file` to `--log`
  * `--out_file` to `--out`
* Specific to `comp` subcommand:
  * `--l` to `--pred`
  * `--r` to `--gt`
  * `--p` to `--alpha`

### Fixed

* **⚠️ Breaking changes:** (`eval` subcommand) Recall, precision and F1 statistics when at least one bin collection is empty.
* **⚠️ Breaking changes:** (`eval` subcommand) Individual recall, precision and F1 statistics column order in TSV
