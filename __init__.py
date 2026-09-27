"""
BSAI-ComfyUI-AimDo-Fix
======================

Purpose
-------
On ComfyUI 0.37.x, the new ``comfy_aimdo`` memory/compiler path (enabled by default
when ``--cuda-malloc`` is passed and ``--disable-comfy-compiler`` is *not*) can crash
the very first sampling step of Qwen Image 2.1 with:

    RuntimeError: aimdo memory compile error
      (comfy_aimdo/malloc_graph.py -> _call -> raise)

This happens because the C-side malloc graph fails to compile for this model /
patch combination. ComfyUI already ships an official bypass: launch with
``--disable-comfy-compiler``.

This plugin reproduces that bypass **at runtime**, as early as possible during
custom-node import, so a machine that cannot easily edit its launcher .bat can
just install / update this node and pull the fix.

It registers NO workflow nodes. It only flips internal switches.

The three layers of defense (all idempotent, all wrapped in try/except):
  1. comfy.cli_args.args.disable_comfy_compiler = True
  2. comfy.memory_management.aimdo_enabled = False
  3. comfy.model_prefetch.malloc_graph_enabled = lambda device: False
"""

import logging

_LOG = logging.getLogger("BSAI-AimDo-Fix")


def _apply_aimdo_disable():
    patched = []

    # Layer 1: the CLI arg that malloc_graph_enabled() itself reads on every call.
    try:
        from comfy.cli_args import args
        args.disable_comfy_compiler = True
        patched.append("args.disable_comfy_compiler=True")
    except Exception as e:  # pragma: no cover - defensive
        _LOG.warning("[BSAI-AimDo-Fix] could not set disable_comfy_compiler: %r", e)

    # Layer 2: the module-level master switch in memory_management.
    try:
        import comfy.memory_management as _mm
        _mm.aimdo_enabled = False
        patched.append("memory_management.aimdo_enabled=False")
    except Exception as e:  # pragma: no cover - defensive
        _LOG.warning("[BSAI-AimDo-Fix] could not set aimdo_enabled: %r", e)

    # Layer 3: hard-override the predicate every caller consults.
    # Callers use the form  comfy.model_prefetch.malloc_graph_enabled(device),
    # so replacing the attribute on the module covers all external call sites.
    try:
        import comfy.model_prefetch as _mp
        _mp.malloc_graph_enabled = lambda device: False  # noqa: E731
        patched.append("model_prefetch.malloc_graph_enabled=>False")
    except Exception as e:  # pragma: no cover - defensive
        _LOG.warning("[BSAI-AimDo-Fix] could not override malloc_graph_enabled: %r", e)

    if patched:
        _LOG.info(
            "[BSAI-AimDo-Fix] comfy compiler / aimdo malloc graph disabled at runtime (%s). "
            "Equivalent to --disable-comfy-compiler. This prevents "
            "'RuntimeError: aimdo memory compile error' on Qwen Image 2.1 / H3 sampling.",
            ", ".join(patched),
        )


_apply_aimdo_disable()

# This is a launch-time compatibility shim; it contributes no nodes.
NODE_CLASS_MAPPINGS = {}
WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS"]
