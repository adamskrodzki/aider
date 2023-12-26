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
from .refinement_prompts import preliminary_message_improvement_prompt
from .refinement_prompts import system_message


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
    perform_refinement = False  # Attribute to control whether to perform refinement

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
        perform_refinement=False,  # Attribute to control whether to perform refinement
    ):
        self.client = client
        self.perform_refinement = perform_refinement  # Attribute to control whether to perform refinement
        ...
