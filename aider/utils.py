import os
import tempfile
from pathlib import Path

import git

from aider.dump import dump  # noqa: F401


class IgnorantTemporaryDirectory:
    def __init__(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def __enter__(self):
        return self.temp_dir.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.temp_dir.__exit__(exc_type, exc_val, exc_tb)
        except (OSError, PermissionError):
            pass  # Ignore errors (Windows)


class ChdirTemporaryDirectory(IgnorantTemporaryDirectory):
    def __init__(self):
        try:
            self.cwd = os.getcwd()
        except FileNotFoundError:
            self.cwd = None

        super().__init__()

    def __enter__(self):
        res = super().__enter__()
        os.chdir(self.temp_dir.name)
        return res

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cwd:
            try:
                os.chdir(self.cwd)
            except FileNotFoundError:
                pass
        super().__exit__(exc_type, exc_val, exc_tb)


class GitTemporaryDirectory(ChdirTemporaryDirectory):
    def __enter__(self):
        dname = super().__enter__()
        self.repo = make_repo(dname)
        return dname

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.repo
        super().__exit__(exc_type, exc_val, exc_tb)


def make_repo(path=None):
    if not path:
        path = "."
    repo = git.Repo.init(path)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "testuser@example.com").release()

    return repo


def safe_abs_path(res):
    "Gives an abs path, which safely returns a full (not 8.3) windows path"
    res = Path(res).resolve()
    return str(res)


def show_messages(messages, title=None, functions=None) -> str:
    output = []
    if title:
        title_output = f"{title.upper()} {'*' * 50}"
        print(title_output)
        output.append(title_output)

    for msg in messages:
        role = msg["role"].upper()
        content = msg.get("content")
        if content:
            for line in content.splitlines():
                line_output = f"{role} {line}"
                print(line_output)
                output.append(line_output)
        content = msg.get("function_call")
        if content:
            func_output = f"{role} {content}"
            print(func_output)
            output.append(func_output)

    if functions:
        functions_output = dump(functions)
        print(functions_output)
        output.append(functions_output)

    return "\n".join(output)
