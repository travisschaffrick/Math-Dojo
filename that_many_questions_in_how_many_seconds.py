import sympy
import random


# Pro-league coding right here

def add(a, b):
    return a + b


def sub(a, b):
    return a - b


def frac(a, b):
    return 1 if b == 0 else a / b


def mult(a, b):
    return a * b


# Heh ... now the fun stars

# For latex rendering use following preamble:
# \newcommand{\add}[2]{#1 + #2}
# \newcommand{\sub}[2]{#1 - #2}
# \newcommand{\mult}[2]{#1 \times #2}

def generate_question(curr_layer: int, max_layers: int, highest_layer: int) -> tuple[str, str, float, int]:
    # Probabilities for choosing each operation: add, sub, frac (division), mult
    chances = [0.35, 0.35, 0.15, 0.15]
    latex_operations = ["add", "sub", "frac", "mult"]
    # Two container styles for LaTeX: absolute value bars or parentheses
    latex_containers = [(r"\left|", r"\right|"), (r"\left(", r"\right)")]

    # Select an operator based on weighted probabilities
    operator_index = random.choices(range(len(latex_operations)), weights=chances)[0]
    latex_operator = latex_operations[operator_index]

    # Select a container style, more likely to be parentheses
    container_index = random.choices(range(len(latex_containers)), weights=[0.15, 0.85])[0]
    latex_container = latex_containers[container_index]

    # Helper to wrap negative integers in parentheses for expression evaluation
    def format_num_expr(n):
        return f"({n})" if isinstance(n, int) and n < 0 else str(n)

    # Helper to wrap negative integers in parentheses for LaTeX formatting
    def format_num_latex(n):
        return f"({n})" if isinstance(n, int) and n < 0 else str(n)

    # Generate 'a':
    # 40% chance to generate a nested expression if we have not reached max depth
    if random.random() < 0.40 and curr_layer < max_layers:
        # Recursive call to generate a nested question
        a, a_latex, _, highest_layer = generate_question(curr_layer + 1, max_layers, max(curr_layer + 1, highest_layer))
    else:
        # Otherwise generate a simple integer number for 'a'
        if random.random() < 0.55:
            a = random.randint(7, 25)  # Medium sized number
        else:
            a = random.randint(1, 7)   # Small sized number
        # 25% chance 'a' is negative
        if random.random() < 0.25:
            a *= -1
        # Format 'a' for LaTeX display (wrap negatives in parentheses)
        a_latex = format_num_latex(a)

    # Generate 'b' with same logic as 'a'
    if random.random() < 0.40 and curr_layer < max_layers:
        b, b_latex, _, highest_layer = generate_question(curr_layer + 1, max_layers, max(curr_layer + 1, highest_layer))
    else:
        if random.random() < 0.55:
            b = random.randint(7, 25)
        else:
            b = random.randint(1, 7)
        if random.random() < 0.25:
            b *= -1
        b_latex = format_num_latex(b)

    # Prepare 'a' and 'b' for symbolic evaluation, wrapping negative ints in parentheses
    # This ensures expressions like -5 are parsed as (-5) in eval, avoiding syntax errors
    a_expr = format_num_expr(a) if isinstance(a, int) else a
    b_expr = format_num_expr(b) if isinstance(b, int) else b

    # Build the Python expression string to evaluate
    # If container is absolute value, wrap expression in abs()
    if latex_container[0] == r"\left|":
        symbolic_fragment = f"abs({latex_operator}({a_expr}, {b_expr}))"
    else:
        symbolic_fragment = f"{latex_operator}({a_expr}, {b_expr})"

    # Build the LaTeX string representation using custom macros and selected container
    latex_fragment = f"{latex_container[0]}\\{latex_operator}{{{a_latex}}}{{{b_latex}}}{latex_container[1]}"

    # Define safe environment to evaluate expression using custom functions (add, sub, frac, mult, abs)
    safe_env = {"add": add, "sub": sub, "frac": frac, "mult": mult, "abs": abs}

    # Evaluate the symbolic expression securely in the restricted environment
    answer = eval(symbolic_fragment, {"__builtins__": None}, safe_env)

    # Return the expression string, LaTeX representation, computed answer, and max recursion depth reached
    return symbolic_fragment, latex_fragment, answer, highest_layer

