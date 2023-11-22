# Work Hour Manager (whm)

Work Hour Manager (whm) is a simple command-line application designed to help manage and track work hours efficiently, without too much information pollution.
## Table of Contents

- [Commands](#commands)
  - [Initialize](#initialize)
  - [Help](#help)
  - [New Entry](#new-entry)
  - [End Timer](#end-timer)
  - [Search](#search)
  - [Export](#export)
- [Example](#example)

## Commands

### Initialize

- **Usage:** `whm i [y]`
- **Description:** Initializes the application, creates the necessary directory, and SQLite database. Use `y` to confirm and overwrite everything.

```bash
$ whm i y
```

### Help

- **Usage:** `whm h`
- **Description:** Displays help information for each command.

```bash
$ whm h
```

### New Entry

- **Usage:** `whm n <name> [<group>] [<hour>]`
- **Description:** Adds a new entry to the database with the provided name, group, and hour values. Group and hour are optional.

```bash
$ whm n Meeting ProjectX 2.5
```

### End Timer

- **Usage:** `whm e`
- **Description:** Ends the currently running timer.

```bash
$ whm e
```

### Search

- **Usage:** `whm s [<date> [<date2>] [<group>]]`
- **Description:** Searches and displays entries based on the specified date, date range, and/or group.

```bash
$ whm s 01-01-2023 31-12-2023 ProjectY
```

```bash
$ whm s 01-01-2023 31-12-2023
```

```bash
$ whm s 01-01-2023
```

```bash
$ whm s ProjectY
```

```bash
$ whm s
```

### Export

- **Usage:** `whm x <output_folder>`
- **Description:** Exports the database to a PDF file in the specified output folder, if nothing is specified, it exports to the current directory.

```bash
$ whm x /path/to/output/folder
```

