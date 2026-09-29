# keplertool — CLI Usage Manual

This is the manual for `keplertool`, the command-line tool that ships with
the `kepler-acp-test` repository. It is implemented elsewhere in the repo
(see `keplertool/`), so this document stays at the interface level: what you
type, what it prints, and what its exit code means.

## Usage

The general form of a `keplertool` invocation is:

    keplertool [options] [name] [value]

- `name` — positional operand naming the record or resource the tool should
  operate on. The exact spelling of accepted names is defined by the
  implementation in `keplertool/`; this manual does not enumerate them.
- `value` — optional second positional operand, when the chosen name needs
  one.
- Every long option has a short, single-dash equivalent.

## Options

| Option | Short form | Meaning |
| --- | --- | --- |
| `--b <B>` | `-b <B>` | Secondary value for the operation, style `--b`-style flag. Placeholder for the real flags implemented in `keplertool/`. |
| `--help` | `-h` | Print a help message describing the interface and exit successfully. |

Options expecting a value take it as the next shell word (`--b 3` — the `=`
form is also accepted) and this manual does not constrain what any value
means; the implementation owns that.

## First command to try

The canonical way to see the interface as the tool itself presents it:

```bash
keplertool --help
```

Run it from any directory: the help screen lists the accepted names, options
and their value forms, and exits with status `0`. When in doubt between this
manual and the `--help` output, trust the `--help` output — it cannot drift
from the code the way a manual can.

## Exit status

| Exit status | Meaning |
| --- | --- |
| `0` | The requested operation completed successfully (including `-h`/`--help`). |
| non-zero | The operation failed; check stderr for the diagnostic. |

## Error handling

On failure, `keplertool` writes a diagnostic to stderr and exits non-zero;
nothing is printed to stdout on a failed run. Script against it with the
usual shell conventions — rely on the exit code, not on parsing stderr.
