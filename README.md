# NFA to DFA Converter (Subset Construction)

Assignment 2 of **SI2002 Formal Languages**. The program reads one or more nondeterministic finite automata (NFAs) from standard input and, for each one, prints the transition table of an equivalent deterministic finite automaton (DFA), built with the Subset Construction from Kozen (1997), Lecture 6.

## 1. Student information

| Field | Value |
|-------|-------|
| Students | Jerónimo Ledesma & Katherine Nocua|
| Class number | SI2002 |
| Course | SI2002 Formal Languages |
| Professor | Sergio Ramírez Rico |
| University | EAFIT |
| Delivery date | 20/09/2026 |

## 2. Environment used

| Item | Version |
|------|---------|
| Operating system | Windows 10 Pro |
| Programming language | Python (3.14.3 |
| Editor | Visual Studio Code |
| Terminal used in VS Code | [ Command Prompt / PowerShell ] |
| Extra libraries | None (standard library only: `sys`, `re`, `math`, `html`, `collections`, `pathlib`) |

Nothing has to be installed: no `pip install` and no virtual environment.

## 3. Files in this delivery

| File | Purpose |
|------|---------|
| `subset_construction.py` | The whole program: parser, subset construction, console output and the optional HTML report. |
| `README.md` | This document. |
| `run.py` | needed to execute the file |
| `ìnput.txt` | input file to change the NFA values |
| `output.html`| shows an aesthetic version of the program |

## 4. Running the program

The program does not open files by itself and prints no prompt: it reads **standard input**, so you must redirect an input file into it (see section 5 for the format). Open the project folder in VS Code (**File > Open Folder**) and open a terminal (**Terminal > New Terminal**). The prompt shows which shell you have:

- `C:\...>` means **Command Prompt (CMD)**.
- `PS C:\...>` means **PowerShell**.

You can change the shell with the arrow next to the `+` button of the terminal panel, or by typing `cmd` or `powershell`.

### 4.1 Console output only

| Shell | Command |
|-------|---------|
| CMD | `python subset_construction.py < input.txt` |
| PowerShell | `Get-Content input.txt | python subset_construction.py` |

PowerShell does not support the `<` operator, and CMD does not know `Get-Content`. If `python` is not recognized, try `py`.

### 4.2 Console output plus the HTML report (optional feature)

| Shell | Command |
|-------|---------|
| CMD | `python subset_construction.py --html output.html < input.txt` |
| PowerShell | `Get-Content input.txt | python subset_construction.py --html output.html` |

Then open the report with `start output.html` or by double-clicking the file. The report is only created when `--html` is given, Use "start output.html" on the terminal to execute.

### 4.3 Typing the input by hand

Run `python subset_construction.py`, paste the input lines, and finish with `Ctrl+Z` then `Enter` (Windows). The result appears after that.

### 4.4 Notes about the Run button (▶) of VS Code

The button only starts the program, which then waits for input that never ends, so it seems to do nothing. Press `Ctrl+C` to stop it and use one of the commands above. To clear the terminal use `cls` (works in both CMD and PowerShell).

[ Add here any other way you run the program, or a link to a demo video (optional) ]

## 5. Input format

```
c                 number of cases, c > 0
```

Then, repeated for each case:

```
n                 number of states; the states are 1, 2, ..., n
S                 initial states, separated by blanks
a b ...           alphabet (lowercase Latin letters), separated by blanks
F                 final states, separated by blanks
row 1             one line per state, in order
...
row n
```

- The empty set is written `0`. For example, an automaton without final states has `0` as its final-states line.
- A row starts with the state number and continues with one cell per symbol, in the same order as the alphabet line. A cell is `0` or a set such as `{1 5}`.

Example (the automaton from the assignment, with `S = {3, 5}` and `F = {1, 4}`):

```
1
5
3 5
a b
1 4
1 {1 5} 0
2 {1} 0
3 {2 4} 0
4 0 {5}
5 {1 5} {4}
```

## 6. Output format

For every case the program prints one table, with no blank lines between cases and nothing else:

- The first line lists the alphabet symbols (one column each).
- Each next line is a DFA state: a marker column, the state name and the target state for each symbol.
- `->` marks the initial state and `<-` marks a final state. A state that is both shows `-><-`.
- Each DFA state is named after the set of NFA states it stands for, for example `{1 2 4 5}`. The empty set is printed as `0`.
- Only states reachable from the initial state are printed, in the order in which they are discovered.

Output for the example of section 5:

```
             a         b
-> {3 5}     {1 2 4 5} {4}
<- {1 2 4 5} {1 5}     {4 5}
<- {4}       0         {5}
<- {1 5}     {1 5}     {4}
<- {4 5}     {1 5}     {4 5}
   0         0         0
   {5}       {1 5}     {4}
```

## 7. How the algorithm works

Let the NFA be `N = (Q, Σ, Δ, S, F)`. The program builds the DFA `M` in these steps:

1. **Parse.** Each case is stored as a dictionary that maps every `(state, symbol)` pair to a set of states.
2. **Start state.** The initial state of `M` is the whole set `S`.
3. **Transition rule.** For a DFA state `A` (a set of NFA states) and a symbol `a`, the next state is `Δ(q, a)` united over every `q` in `A`.
4. **Exploration.** A queue starts with `S`. Each time a new set appears as a target it is stored and queued, and the loop ends when the queue is empty. This is a breadth-first search, so only reachable states are built.
5. **Final states.** A DFA state is final when it shares at least one element with `F`.
6. **Determinism.** Symbols are read in alphabet order and states are numbered by discovery order, so the same input always gives the same output.

Worked step from the example: `δ({3,5}, a) = Δ(3,a) ∪ Δ(5,a) = {2,4} ∪ {1,5} = {1,2,4,5}`.

In the worst case the DFA has up to `2^n` states, but reachable states are usually far fewer (here 7 out of 32).

[ Add here, in your own words, why the DFA accepts the same language as the NFA ]

## 8. Optional feature: HTML report

With `--html`, the program also writes a self-contained web page (no internet or libraries needed). For each case it shows:

- a drawing of the DFA, with an arrow into the initial state, double rings on final states and a dashed circle for the empty set;
- the DFA transition table;
- a collapsible copy of the input NFA.

[ Add screenshots or extra notes about the diagrams here ]

## 9. Extra test

Input (NFA that accepts the strings ending in `ab`):

```
1
3
1
a b
3
1 {1 2} {1}
2 0 {3}
3 0 0
```

Expected output:

```
         a     b
-> {1}   {1 2} {1}
   {1 2} {1 2} {1 3}
<- {1 3} {1 2} {1}
```

[ Add more of your own test cases here ]

## 10. Limitations and assumptions

- States are the numbers `1..n` and the alphabet is made of lowercase letters, as stated in the assignment.
- The input must follow the format of section 5; there is no error handling for malformed files.
- [ Add other limitations or remarks here ]

## Reference

Kozen, Dexter C. (1997). *Automata and Computability*. 1st. Berlin, Heidelberg: Springer-Verlag. https://doi.org/10.1007/978-1-4612-1844-9
