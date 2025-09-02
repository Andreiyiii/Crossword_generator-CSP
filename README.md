# Crossword Generator (CSP)

A crossword puzzle generator that uses **Constraint Satisfaction Problem (CSP)** techniques to fill a given crossword grid with words from a given vocabulary enforcing constraints such as word length and overlapping letters.

## Features
- Analyze a crossword structure and a set of words.
- Uses **CSP techniques**:
  - Node consistency
  - Arc consistency (AC-3)
  - Backtracking search
- Print the solution.
- Optionally save the crossword as image.

## Usage

```bash
python generate.py structure.txt words.txt [output.png]