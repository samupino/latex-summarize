import os
import re
import argparse


class LatexParser:

    def __init__(self, envs_to_track: list):
        self.envs_to_track = envs_to_track

    def check_start_chapter(self, line: str):
        """If line is a chapter declaration return chapter name, else None."""
        pattern = r"chapter\{(.+)\}"
        match = re.search(pattern, line)
        if (match):
            return match.groups()[0]
        else:
            return None

    def check_start_section(self, line: str):
        """If line is a section declaration return section name, else None."""
        pattern = r"section\{(.+)\}"
        match = re.search(pattern, line)
        if (match):
            return match.groups()[0]
        else:
            return None
    
    def check_start_appendix(self, line: str):
        """If line is an appendix declaration return 'Appendix: NAME', else None."""
        pattern = r"append(\[.*\])?\{(.+)\}"
        match = re.search(pattern, line)
        if (match):
            return "Appendix: " + match.groups()[-1]
        else:
            return None

    def check_begin_env(self, line: str):
        """If line is an environment declaration of interest return env name, else None."""
        pattern = r"begin\{(" + "|".join(self.envs_to_track) + r")\}"
        foundBegin = re.search(pattern, line)
        if (foundBegin):
            environment = foundBegin.groups()[0]
            return environment
        else:
            return None

    def check_end_env(self, line: str, current_environment: str) -> bool:
        """Return if line declares the end of the specified environment."""
        pattern = r"end\{(" + current_environment + r")\}"
        if (re.search(pattern, line)):
            return True
        else:
            return False

    def check_file_include(self, line: str):
        """If line is an include/input return the filepath, else None"""
        pattern = r"(input|include)\{(.+)\}"
        match = re.search(pattern, line)
        if (match):
            file_rel_path = match.groups()[1]
            if (not file_rel_path.endswith(".tex")):
                file_rel_path += ".tex"
            return file_rel_path
        else:
            return None


def print_env(out_file, current_chapter, current_section, line: str):
    """Print line on file, possibly preceded by section declarations."""
    if (current_chapter):
        out_file.write("\\section*{"+current_chapter+"}\n\n")

    if (current_section):
        out_file.write("\\subsection*{"+current_section+"}\n\n")
        current_section = None
    out_file.write(line)


def find_and_copy_envs(out_file, tex_path: str, p: LatexParser):
    """Analyze the text line by line and copy the desired envs in the out file."""

    current_chapter = None
    current_section = None
    current_environment = None
    nesting_level = 0
    tex_main_dir = os.path.dirname(tex_path)

    with open(tex_path) as input_file:
        out_file.write("")
        lines = input_file.readlines()

    for line in lines:

        found_include = p.check_file_include(line)
        if (found_include):
            # Enter the new file recursively, when finished move to the next line
            included_path = os.path.join(tex_main_dir, found_include)
            find_and_copy_envs(out_file, included_path, p)
            continue

        if (current_environment is None):
            # If we are not in one of the specified environments.

            found_environment = p.check_begin_env(line)
            found_chapter = p.check_start_chapter(line) or p.check_start_appendix(line)
            found_section = p.check_start_section(line)

            if (found_environment):
                # Line matches the pattern 'begin{ENV}' is found, with ENV being one of the
                # specified environments.
                print_env(out_file, current_chapter, current_section, line)
                current_environment = found_environment
                current_chapter = None
                current_section = None
            elif (found_chapter):
                # Line matches the pattern "chapter{...}"
                current_chapter = found_chapter
            elif (found_section):
                # Line matches the pattern "section{...}"
                current_section = found_section

        else:
            # If we are already inside one of the specified environments.

            out_file.write(line)

            found_environment = p.check_begin_env(line)
            if (found_environment == current_environment):
                nesting_level += 1
            
            if (p.check_end_env(line, current_environment)):
                # Line matches the pattern "end{ENV}" where ENV is the current environment.
                if (nesting_level > 0):
                    nesting_level -= 1
                if (nesting_level == 0):
                    current_environment = None
                    out_file.write("\n")


def main(tex_main: str, out_path: str, envs_to_copy: list):

    p = LatexParser(envs_to_copy)
    with open(out_path, "w") as out_file:
        find_and_copy_envs(out_file, tex_main, p)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate a LaTeX file copying only specified envs from a source project.")

    parser.add_argument("tex_main", metavar="TEX_MAIN", type=str,
                        help="main .tex file containing document begin-end")
    parser.add_argument("-o", dest="out_file", type=str, default="./summarized.tex",
                        help="where to save the generated tex code (default './summary.tex')")
    parser.add_argument("envs", metavar="ENV", nargs="+", type=str,
                        help="names of latex environments to copy in the generated .tex")

    args = parser.parse_args()

    main(args.tex_main, args.out_file, args.envs)
