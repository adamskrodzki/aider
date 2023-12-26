# entire file content ...
# ... goes in between
#!/usr/bin/env python

import hashlib
import json
import os
import sys
import threading
import time
import traceback
from json.decoder import JSONDecodeError
from pathlib import Path

import openai
from jsonschema import Draft7Validator
from rich.console import Console, Text
from rich.live import Live
from rich.markdown import Markdown

from aider import models, prompts, utils
from aider.commands import Commands
from aider.history import ChatSummary
from aider.io import InputOutput
from aider.repo import GitRepo
from aider.repomap import RepoMap
from aider.sendchat import send_with_retries

from ..dump import dump  # noqa: F401
from .refinement_messages import preliminary_message_improvement_prompt
from .refinement_messages import system_message


class MissingAPIKeyError(ValueError):
    pass


class ExhaustedContextWindow(Exception):
    pass


def wrap_fence(name):
    return f"<{name}>", f"</{name}>"


class Coder:
    client = None
    abs_fnames = None
    repo = None
    last_aider_commit_hash = None
    last_asked_for_commit_time = 0
    repo_map = None
    functions = None
    total_cost = 0.0
    num_exhausted_context_windows = 0
    num_malformed_responses = 0
    last_keyboard_interrupt = None
    max_apply_update_errors = 3
    edit_format = None
    perform_refinement = False  # Attribute to control whether to perform message refinement

    @classmethod
    def create(
        self,
        main_model=None,
        edit_format=None,
        io=None,
        client=None,
        skip_model_availabily_check=False,
        **kwargs,
    ):
        from . import EditBlockCoder, UnifiedDiffCoder, WholeFileCoder

        if not main_model:
            main_model = models.GPT4

        if not skip_model_availabily_check and not main_model.always_available:
            if not check_model_availability(io, client, main_model):
                fallback_model = models.GPT35_1106
                if main_model != models.GPT4:
                    io.tool_error(
                        f"API key does not support {main_model.name}, falling back to"
                        f" {fallback_model.name}"
                    )
                main_model = fallback_model

        if edit_format is None:
            edit_format = main_model.edit_format

        if edit_format == "diff":
            return EditBlockCoder(client, main_model, io, **kwargs)
        elif edit_format == "whole":
            return WholeFileCoder(client, main_model, io, **kwargs)
        elif edit_format == "udiff":
            return UnifiedDiffCoder(client, main_model, io, **kwargs)
        else:
            raise ValueError(f"Unknown edit format {edit_format}")

    def __init__(
        self,
        client,
        main_model,
        io,
        fnames=None,
        git_dname=None,
        pretty=True,
        show_diffs=False,
        auto_commits=True,
        dirty_commits=True,
        dry_run=False,
        map_tokens=1024,
        verbose=False,
        assistant_output_color="blue",
        code_theme="default",
        stream=True,
        use_git=True,
        voice_language=None,
        aider_ignore_file=None,
        perform_refinement=False,
    ):
        self.client = client

        if not fnames:
            fnames = []

        if io is None:
            io = InputOutput()

        self.chat_completion_call_hashes = []
        self.chat_completion_response_hashes = []
        self.need_commit_before_edits = set()

        self.verbose = verbose
        self.abs_fnames = set()
        self.cur_messages = []
        self.done_messages = []

        self.io = io
        self.stream = stream

        if not auto_commits:
            dirty_commits = False

        self.auto_commits = auto_commits
        self.dirty_commits = dirty_commits
        self.assistant_output_color = assistant_output_color
        self.code_theme = code_theme
        self.perform_refinement = perform_refinement  # Set the perform_refinement attribute

        self.dry_run = dry_run
        self.pretty = pretty

        if pretty:
            self.console = Console()
        else:
            self.console = Console(force_terminal=False, no_color=True)

        self.main_model = main_model

        self.io.tool_output(f"Model: {main_model.name} using {self.edit_format} edit format")

        self.show_diffs = show_diffs

        self.commands = Commands(self.io, self, voice_language)

        for fname in fnames:
            fname = Path(fname)
            if not fname.exists():
                self.io.tool_output(f"Creating empty file {fname}")
                fname.parent.mkdir(parents=True, exist_ok=True)
                fname.touch()

            if not fname.is_file():
                raise ValueError(f"{fname} is not a file")

            self.abs_fnames.add(str(fname.resolve()))

        if use_git:
            try:
                self.repo = GitRepo(
                    self.io, fnames, git_dname, aider_ignore_file, client=self.client
                )
                self.root = self.repo.root
            except FileNotFoundError:
                self.repo = None

        if self.repo:
            rel_repo_dir = self.repo.get_rel_repo_dir()
            num_files = len(self.repo.get_tracked_files())
            self.io.tool_output(f"Git repo: {rel_repo_dir} with {num_files} files")
        else:
            self.io.tool_output("Git repo: none")
            self.find_common_root()

        if main_model.use_repo_map and self.repo and self.gpt_prompts.repo_content_prefix:
            self.repo_map = RepoMap(
                map_tokens,
                self.root,
                self.main_model,
                io,
                self.gpt_prompts.repo_content_prefix,
                self.verbose,
            )

        if map_tokens > 0:
            self.io.tool_output(f"Repo-map: using {map_tokens} tokens")
        else:
            self.io.tool_output("Repo-map: disabled because map_tokens == 0")

        for fname in self.get_inchat_relative_files():
            self.io.tool_output(f"Added {fname} to the chat.")

        self.summarizer = ChatSummary(
            self.client,
            models.Model.weak_model(),
            self.main_model.max_chat_history_tokens,
        )

        self.summarizer_thread = None
        self.summarized_done_messages = []

        # validate the functions jsonschema
        if self.functions:
            for function in self.functions:
                Draft7Validator.check_schema(function)

            if self.verbose:
                self.io.tool_output("JSON Schema:")
                self.io.tool_output(json.dumps(self.functions, indent=4))

    # ... rest of code ...
