"""
propositions.py 1.0
@author: github.com/alin-c

Displays the truth table of a given complex proposition and determines
its type:
- tautology: all interpretations are true;
- satisfiable: it exists a true interpretation;
- contingent: it exists at least one true and one false interpretation;
- unsatisfiable: all interpretations are false.
"""

import re
import itertools

fixed_chars = {
    "~": "¬",
    "&": " ∧ ",
    "|": " ∨ ",
    "+": " ⊕  ",    # 2 spaces needed after it, for correct display
    ">": " → ",
    "<": " ≡ ",
    "(": "(",
    ")": ")",
}


class Proposition:
    """
    The representation of a proposition and of its supported operators.
    """

    def __init__(self, value=bool(), name=str()):
        self.value = True if value is not False else False
        self.name = name

    def __invert__(self):
        """
        Negation operator; displayed as ¬
        """
        value = True if self.value is False else False
        name = f"¬{self.name}"
        return Proposition(value, name)

    def __and__(self, other):
        """
        Conjunction operator; displayed as ∧
        """
        value = True if self.value and other.value else False
        name = f"{self.name} ∧ {other.name}"
        return Proposition(value, name)

    def __or__(self, other):
        """
        Disjunction operator; displayed as ∨
        """
        value = True if self.value or other.value else False
        name = f"{self.name} ∨ {other.name}"
        return Proposition(value, name)

    def __add__(self, other):
        """
        Exclusive disjunction operator; displayed as ⊕
        """
        value = False if self.value == other.value else True
        name = f"{self.name} ⊕ {other.name}"
        return Proposition(value, name)

    def __gt__(self, other):
        """
        Implication operator; displayed as →
        """
        value = False if (self.value is True) and (
            other.value is False) else True
        name = f"{self.name} → {other.name}"
        return Proposition(value, name)

    def __lt__(self, other):
        """
        Equivalence operator; displayed as ≡
        """
        value = True if self.value == other.value else False
        name = f"{self.name} ≡ {other.name}"
        return Proposition(value, name)


def extract_simple_props(input_string):
    """
    Adds Proposition objects from each distinct letter to the global scope
    and into a sorted global list.
    """
    global simple_props
    simple_props = []

    letters = set(re.findall(r"([a-z])", input_string))
    letters = sorted(list(letters))

    for e in letters:
        if eval(f"'{e}' not in [prop.name for prop in simple_props]"):
            exec(f"global {e}; \
                {e} = Proposition(name = '{e}'); \
                simple_props.append({e})")


def extract_tokens(input_string):
    """
    Returns a dictionary of tokens which represent the groups from parantheses
    and their positions in the string.
    Tokens are of type (position: group); subgroups are represented by key.
    """
    tokens = dict()
    counter = 0

    while True:
        groups = re.findall(r"(~?\([^()]*?\))", input_string)
        if groups:
            for i in range(len(groups)):
                tokens[counter] = groups[i]
                input_string = input_string.replace(groups[i], f"{counter}")
                counter += 1
        else:
            break

    return [input_string, tokens]


def decompress_tokens(input_string, tokens):
    """
    Rebuilds the string used for tokenization, using the output from
    extract_tokens().
    """
    while True:
        match = re.search(r"(\d+?)", input_string)
        if not match:
            return input_string
        else:
            i = match.group(1)
            input_string = input_string.replace(i, tokens[1][int(i)])


def get_table():
    """
    Generates a list with the elements of the truth table, using
    simple_props and tokens.
    """
    table_header = (
        [prop.name for prop in simple_props]
        + [decompress_tokens(tokens[1][token], tokens) for token in tokens[1]]
        + [initial_string]
    )
    table = [table_header]

    truth_combinations = list(
        itertools.product([True, False], repeat=len(simple_props))
    )

    for row_index in range(len(truth_combinations)):
        table.append(list(truth_combinations[row_index]))
        for i in range(len(simple_props)):
            simple_props[i].value = truth_combinations[row_index][i]
        for i in range(len(simple_props), len(table_header)):
            code = table_header[i]
            table[row_index + 1].append(eval(f"({code}).value"))

    return table


def display_table(table):
    """
    Displays the truth table, using the appropriate symbols and formatting.
    """
    result = "\n\t"
    empty = ""
    column_width = []

    table.insert(1, ["" for i in table[0]])
    for i in range(len(table)):
        for j in range(len(table[i])):
            # separator
            separator = "\n\t" if j == (len(table[i]) - 1) else "|"
            if i == 0:  # header
                header = operator_replacer(table[0][j])
                element = f"{header:^{len(header)+2}}"
                result += element + separator
                column_width.append(len(element))
            elif i == 1:  # separation line
                result += f"{empty:-^{column_width[j]}}" + (
                    "\n\t" if j == (len(table[i]) - 1) else "+"
                )
            else:  # table content
                value = "T" if table[i][j] is True else "F"
                result += f"{value:^{column_width[j]}}" + separator

    return result


def operator_replacer(input_string):
    """
    Replaces the input operator with the ones for proper display.
    """
    for key in fixed_chars.keys():
        input_string = input_string.replace(key, fixed_chars[key])

    return input_string


def get_proposition_type(table):
    """
    Determines the proposition type.
    """
    last_column = []
    j = len(table[1]) - 1
    for i in range(1, len(table)):
        last_column += [table[i][j]]

    result = ""
    if False not in last_column:
        result = "valid (tautology, also satisfiable)"
    elif True not in last_column:
        result = "contradiction (unsatisfiable)"
    elif True in last_column:
        result = "satisfiable"  # never displayed... :)
        if False in last_column:
            result = "contingent (also satisfiable)"

    return result


def proposition_matcher(input_string):
    """
    Validates the input, creates global varaibles for each simple porposition,
    returns an object with the tokens.
    """
    global initial_string

    input_string = re.sub(r"\s", "", input_string.lower())
    if input_string == "":
        print("Input cannot be empty.")
        return False

    initial_string = input_string

    # rapid validation tests:
    patterns = r"""
        (?:(\d)|                # 1 digits
        ([^a-z()~&|+<>])|       # 2 all unallowed characters
        ([a-z]{2,})|            # 3 adjacent letters
        (\([^(~a-z])|           # 4 a group can only begin with: ( ~ or a-z
        ([^a-z)]\))|            # 5 a group can only end with: ) or a-z
        ([a-z)]~)|              # 6 ~ between propositions or at the end
        ([^)a-z][&|+<>]|        # 7 binary operators must have exactly 2 terms
            [&|+<>][^a-z(~]|
            ^[&|+<>]|
            [&|+<>~]$)|
        ([a-z][(]|[)][a-z]))    # 8 parentheses adjacent to letters: a( or )a
    """
    regex = re.compile(patterns, re.X)
    matcher = regex.search(input_string)
    if matcher:
        message = str()
        if matcher.group(1):
            message = f"Input cannot contain digits (ex. {matcher.group(1)})!"
        elif matcher.group(2):
            message = "Input cannot contain unallowed characters (ex." \
                + f" {matcher.group(2)})!"
        elif matcher.group(3):
            message = "Every simple proposition can only be represented by" \
                + f" a single letter! (ex. {matcher.group(3)})!"
        elif matcher.group(4):
            message = "A group can only begin with: ( ~ or letter!" \
                + f" (ex. {matcher.group(4)})!"
        elif matcher.group(5):
            message = "A group can only end with: ) or letter!" \
                + f" (ex. {matcher.group(5)})!"
        elif matcher.group(6):
            message = "~ operator cannot appear between two propositions" \
                + f" or at the end! (ex. {matcher.group(6)})!"
        elif matcher.group(7):
            message = "Binary operators can only have 2 operands!" \
                + f" (ex. {matcher.group(7)})!"
        elif matcher.group(8):
            message = "Parentheses cannot be adjacent to letters: a( or )a!" \
                + f" (ex. {matcher.group(8)})!"
        print(message)
        return False

    tokens = extract_tokens(input_string)
    if re.search(r"[()]", tokens[0]):
        print("Input cannot contain unmatched parentheses!")
        return False
    extract_simple_props(input_string)

    return tokens


def validate_input(input_string):
    """
    Validates input using proposition_matcher().
    """
    while True:
        output = proposition_matcher(input_string)
        if output:
            return output
        else:
            input_string = input(
                "Type valid input (see rules above)!\nTry again:\n")


print(__doc__)
example = """Rules for valid input:
- use a single letter for a simple proposition
- logical operators are:
  ~ (¬ not)
  & (∧ and)
  | (∨ or)
  + (⊕  exclusive or, xor)
  > (→ implies, if)
  < (≡ equivalent, iff)
- allowed characters: spaces, letters, parentheses (round) and listed operators
- parentheses may be nested in other parentheses, but they must be paired
"""
print(example)
while True:
    print("\nType a complex proposition: ")
    tokens = validate_input(input())
    table = get_table()
    print(display_table(table))
    print(f"\nThe proposition is: {get_proposition_type(table)}.")
