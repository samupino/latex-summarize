import os
import re
import argparse


def check_start_chapter(line: str):
    """If line is a chapter declaration return chapter name, else None."""
    pattern = r"chapter\{(.+)\}"
    match = re.search(pattern, line)
    if (match):
        return match.groups()[0]
    else:
        return None


def check_start_section(line: str):
    """If line is a section declaration return section name, else None."""
    pattern = r"section\{(.+)\}"
    match = re.search(pattern, line)
    if (match):
        return match.groups()[0]
    else:
        return None


def check_begin_env(line: str, env_to_replicate: list):
    """If line is an environment declaration of interest return env name, else None."""
    pattern = r"begin\{(" + "|".join(env_to_replicate) + r")\}"
    foundBegin = re.search(pattern, line)
    if (foundBegin):
        environment = foundBegin.groups()[0]
        return environment
    else:
        return None


def check_end_env(line: str, current_environment: str) -> bool:
    """Return if line declares the end of the specified environment."""
    pattern = r"end\{(" + current_environment + r")\}"
    if (re.search(pattern, line)):
        return True
    else:
        return False


def print_env(out_file, current_chapter, current_section, line: str):
    """Print line on file, possibly preceded by section declarations."""
    if (current_chapter):
        out_file.write("\\section*{"+current_chapter+"}\n\n")

    if (current_section):
        out_file.write("\\subsection*{"+current_section+"}\n\n")
        current_section = None
    out_file.write(line)


def find_and_copy_envs(out_file, lines: list, envs_to_copy: list):
    """Analyze the text line by line and copy the desired envs in the out file."""

    current_chapter = None
    current_section = None
    current_environment = None
    nesting_level = 0

    for line in lines:

        if (current_environment is None):
            # If we are not in one of the specified environments.

            found_environment = check_begin_env(line, envs_to_copy)
            found_chapter = check_start_chapter(line)
            found_section = check_start_section(line)

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

            found_environment = check_begin_env(line, envs_to_copy)
            if (found_environment == current_environment):
                nesting_level += 1

            out_file.write(line)
            if (check_end_env(line, current_environment)):
                # Line matches the pattern "end{ENV}" where ENV is the current environment.
                if (nesting_level > 0):
                    nesting_level -= 1
                if (nesting_level == 0):
                    current_environment = None
                    out_file.write("\n")


def main(tex_files_dir: str, out_path: str, envs_to_copy: list):

    tex_files = []
    for filename in os.listdir(tex_files_dir):
        full_path = os.path.join(tex_files_dir, filename)
        if (filename.endswith(".tex") and full_path != out_path):
            tex_files.append(full_path)

    with open(out_path, "w") as out_file:

        out_file.write("")
        for tex_file in tex_files:
            with open(tex_file) as f:
                lines = f.readlines()
            find_and_copy_envs(out_file, lines, envs_to_copy)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate a LaTeX file copying only specified envs from a source project.")

    parser.add_argument("-d", dest="tex_dir", type=str, default="./",
                        help="directory containing the .tex files (default './')")
    parser.add_argument("-o", dest="out_file", type=str, default="./summarized.tex",
                        help="where to save the generated tex code (default './summary.tex')")
    parser.add_argument("envs", metavar="ENV", nargs="+", type=str,
                        help="names of latex environments to copy in the generated .tex")

    args = parser.parse_args()

    main(args.tex_dir, args.out_file, args.envs)
