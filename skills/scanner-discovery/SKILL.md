---
description: Detect available scanners using scanline -list. Returns scanner names for setup/configuration.
---

# Scanner Discovery Skill

Detect and list available scanners on macOS using the `scanline` CLI.

## Usage

```bash
scanline -list
```

## Output Format

The command outputs available scanners in this format:

```
Available scanners:
* Scanner Name 1
* Scanner Name 2
Done
```

## Parsing

- Scanner names are prefixed with `*`
- Ignore lines that don't start with `*`
- Strip the `*` prefix and whitespace to get the scanner name

## Example

```bash
$ scanline -list
Available scanners:
* Brother MFC-L2800DW
Done
```

Result: `["Brother MFC-L2800DW"]`

## Notes

- `scanline -list` can take 5-10 seconds to complete (network scanner discovery)
- Returns exit code 0 on success
- Empty list if no scanners found
