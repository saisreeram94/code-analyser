# Code Analyzer

A Python-based tool for analyzing source code files and providing detailed statistics about code structure, comments, and blank lines. The analyzer supports multiple programming languages and can process both individual files and entire directories.

## Features

- **Multi-language Support:**
  - Java (.java)
  - Python (.py)
  - JavaScript (.js)
  - C (.c, .h)

- **Detailed Analysis:**
  - Line counting by category (code, comments, blank lines)
  - Code breakdown by type:
    - Import statements
    - Class definitions
    - Function/Method definitions
    - Variable declarations
    - Other code

- **Advanced Capabilities:**
  - Memory-efficient processing of large files
  - Parallel processing for directories
  - Support for both single and multi-line comments
  - Human-readable file size formatting

## Installation

1. Ensure you have Python 3.6 or higher installed
2. No additional dependencies required - uses only Python standard library

## Project Structure

```
code-analyzer/
├── config.py         # Language configurations and patterns
├── analyzers.py      # Core analysis logic
├── main.py          # CLI interface and result formatting
└── README.md        # This file
```

## Usage

1. Run the program:
   ```bash
   python main.py
   ```

2. Enter the path when prompted:
   - Can be a single file: `path/to/file.java` Eg. config.py
   - Can be a directory: `path/to/source/code/` Eg. samples
   - Type 'quit' or 'exit' to close the program

## Example Output

```
Source Tree Analysis Summary
================================================================================
Total Files Analyzed: 1

Java Summary:
========================================
Total Files: 1

Language-wide Statistics:
------------------------------
Blank: 3
Comments: 3
Code: 6

Code Breakdown:
--------------------
Import: 1
Class Definition: 1
Function Definition: 1
Variable Declaration: 0
Other Code: 3

Individual File Details for Java:
------------------------------------------------------------
File: Example.java
Path: /path/to/Example.java
Size: 237.00 B
  Blank: 3
  Comments: 3
  Code: 6
  Code Breakdown:
    Import: 1
    Class Definition: 1
    Function Definition: 1
    Variable Declaration: 0
    Other Code: 3
  Total Lines: 12
```

## Features Details

### Language-specific Analysis
- **Java:** Detects imports, class definitions, method definitions, variable declarations
- **Python:** Identifies imports, class definitions, function definitions, variable assignments
- **JavaScript:** Analyzes imports, class definitions, function declarations, variable declarations
- **C:** Processes includes, function definitions, variable declarations

### Performance Features
- Efficient memory usage with chunk-based processing for large files
- Parallel processing for directory analysis
- Progress tracking for large operations

### Analysis Categories
1. **Main Categories:**
   - Blank lines
   - Comments (single and multi-line)
   - Code lines

2. **Detailed Code Breakdown:**
   - Import/Include statements
   - Class definitions
   - Function/Method definitions
   - Variable declarations
   - Other code
