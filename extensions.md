# Extensions

## Validated ideas

### Pandas utilities

**Very good idea.** This matches the library’s current “I keep rebuilding this” purpose. The module should focus on repetitive data-wrangling helpers: loading, cleaning, reshaping, column normalization, null handling, joins, and export helpers.

Good first features:

- dataframe cleaning helpers
- column rename/normalize utilities
- CSV/Excel import presets
- null and dtype normalization
- quick summarization helpers

### scikit-learn utilities

**Good idea, but only if scoped narrowly.** This is useful if it provides small workflow helpers rather than abstractions over the whole ML ecosystem. The best fit is feature preparation, split helpers, metrics wrappers, and repeatable evaluation utilities.

Good first features:

- train/test split presets
- pipeline builder helpers
- feature scaling and encoding shortcuts
- metric bundles for common tasks
- model evaluation reports

## Further extension ideas

### 2. `csvx`

CSV-specific import/export helpers with dialect presets, schema inference, and validation.

### 3. `imagesx`

Small image utilities for resize, crop, convert, metadata read/write, and thumbnail generation.

### 4. `osx`

Filesystem and process helpers for path cleanup, safe temp files, environment loading, and subprocess wrappers.

### 5. `cli` helpers

Reusable command-line scaffolding: argument parsing, color output, progress bars, config loading, and prompt helpers.

### 6. `api` utilities

Request/response helpers for JSON APIs, pagination, retries, rate limiting, and typed payload validation.

### 7. `datax`

General data helpers for dict/list transforms, deduping, grouping, flattening, and batch processing.

## Best next extension

If you want the highest immediate value, I would add **pandas utilities first**, then **Tkinter UI helpers**, then **scikit-learn helpers**.
