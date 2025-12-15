import os
import sys
import argparse
import ast

def process_file(filename, output_path):
    """
    Reads a Python file, removes all comments and docstrings,
    and writes the result to a new file.
    
    The original file is not modified.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_content = f.read()

        try:
            tree = ast.parse(file_content, filename=filename)
        except SyntaxError as e:
            print(f"  Error: Could not parse {filename}. Invalid syntax? {e}")
            return False

        class DocstringRemover(ast.NodeTransformer):
            def _strip_first_expr_doc(self, node):
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(getattr(node.body[0], "value", None), ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    node.body = node.body[1:]
                return node

            def visit_FunctionDef(self, node):
                self.generic_visit(node)
                return self._strip_first_expr_doc(node)

            def visit_AsyncFunctionDef(self, node):
                self.generic_visit(node)
                return self._strip_first_expr_doc(node)

            def visit_ClassDef(self, node):
                self.generic_visit(node)
                return self._strip_first_expr_doc(node)

            def visit_Module(self, node):
                self.generic_visit(node)
                return self._strip_first_expr_doc(node)

        tree = DocstringRemover().visit(tree)
        ast.fix_missing_locations(tree)

        new_content = ast.unparse(tree)
        if not new_content.endswith("\n"):
            new_content += "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return True
        
    except Exception as e:
        print(f"  Error processing {filename}: {e}")
        return False

def main():
    """
    Main function to strip comments/docstrings from a single Python file.
    """
    parser = argparse.ArgumentParser(
        description="Strip comments/docstrings from a Python file."
    )
    parser.add_argument(
        "filepath",
        help="Path to the Python file to process.",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.filepath)

    if not os.path.isfile(input_path):
        print(f"File '{input_path}' not found.")
        return

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_comment_removed{ext or '.py'}"

    print(f"Processing {input_path} -> {output_path}")

    if process_file(input_path, output_path):
        print("Done.")
    else:
        print("Failed.")

if __name__ == "__main__":
    main()
