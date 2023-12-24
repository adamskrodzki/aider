from .wholefile_coder import WholeFileCoder
from .mixtral_wholefile_prompts import MixtralWholeFilePrompts

class MixtralWholeFileCoder(WholeFileCoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpt_prompts = MixtralWholeFilePrompts()
        self.mixtral_optimized = True 

    def apply_edits(self, edits):
        for path, fname_source, new_lines in edits:
            full_path = self.abs_root_path(path)
            new_lines = "".join(new_lines)
            self.io.write_text(full_path, new_lines)
