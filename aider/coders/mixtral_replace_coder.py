import math
import re
from difflib import SequenceMatcher
from pathlib import Path

from ..dump import dump  # noqa: F401
from .base_coder import Coder
from .mixtral_replace_prompts import MixtralReplacePrompts


class MixtralReplaceCoder(EditBlockCoder):
    edit_format = "diff"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpt_prompts = MixtralReplacePrompts()
        self.mixtral_optimized = True 


    def apply_edits(self, edits):
        for path, original, updated in edits:
            full_path = self.abs_root_path(path)
            content = self.io.read_text(full_path)
            original_content = content
            content = do_replace(full_path, content, original, updated, self.fence)
            if content:
                self.io.write_text(full_path, content)
                continue
            print ("Error in edit",path, original, updated)
            raise ValueError(f"""InvalidEditBlock: edit failed!

{path} does not contain the *exact chunk* of SEARCH lines you specified.
Try again.
DO NOT skip blank lines, comments, docstrings, etc!
The SEARCH block needs to be EXACTLY the same as the lines in {path} with nothing missing!

{path} does not contain these {len(original.splitlines())} exact lines in a row:
```
{original}```

current actual content of the file is

```
{original_content}
```
""")

if __name__ == "__main__":
    edit = """
Here's the change:

```text
foo.txt
<<<<<<< HEAD
Two
=======
Tooooo
>>>>>>> updated
```

Hope you like it!
"""
    print(list(find_original_update_blocks(edit)))
