# BSAI-ComfyUI-AimDo-Fix

> ComfyUI 0.37.x launcher-compatibility shim: runtime-disable the `comfy_aimdo`
> memory/compiler graph, equivalent to launching with `--disable-comfy-compiler`.
>
> ComfyUI 0.37.x 启动兼容补丁：在运行时禁用 `comfy_aimdo` 内存图编译器，
> 效果等价于启动参数 `--disable-comfy-compiler`。

---

## English

### What this fixes

On ComfyUI 0.37.x, when launched with `--cuda-malloc` but **without**
`--disable-comfy-compiler`, the new `comfy_aimdo` malloc-graph path can crash the
very first sampling step of Qwen Image 2.1 (and other models that trigger
malloc-graph compilation) with:

```
RuntimeError: aimdo memory compile error
  File ".../site-packages/comfy_aimdo/malloc_graph.py", line 16, in _call
    raise RuntimeError("aimdo memory compile error")
```

Log line just before the crash usually reads:

```
Comfy model compiler graph breaks: 0, rogues: N
```

Root cause: the C-side malloc graph fails to compile for this model / patch
combination. ComfyUI already ships the official bypass — launch with
`--disable-comfy-compiler`. This plugin reproduces that bypass **at runtime**, as
early as possible during custom-node import, so a machine that cannot easily edit
its launcher `.bat` can just install / update this node and pull the fix.

### Install

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/xm6018924/BSAI-ComfyUI-AimDo-Fix.git
```

Restart ComfyUI. No workflow changes needed.

### What it does

It registers **no workflow nodes**. On import it flips three internal switches
(all idempotent, each wrapped in try/except):

1. `comfy.cli_args.args.disable_comfy_compiler = True`
2. `comfy.memory_management.aimdo_enabled = False`
3. `comfy.model_prefetch.malloc_graph_enabled = lambda device: False`

On successful apply you will see one info line in the console:

```
[BSAI-AimDo-Fix] comfy compiler / aimdo malloc graph disabled at runtime (...).
Equivalent to --disable-comfy-compiler.
```

### Requirements

- ComfyUI 0.37.x (the version where `comfy_aimdo` exists). Harmless no-op on older
  versions (the import block just warns and continues).
- No extra pip packages.

### Notes

- This does **not** reduce image quality or change sampling results; it only turns
  off an experimental memory graph that fails to compile on this setup.
- If you can edit your launcher `.bat`, adding `--disable-comfy-compiler` achieves
  the same result without this plugin. The plugin exists for machines where editing
  the bat is inconvenient.

---

## 中文

### 解决什么问题

ComfyUI 0.37.x 在带 `--cuda-malloc` 启动、但**没有**加 `--disable-comfy-compiler`
的机器上，跑 Qwen Image 2.1（以及其他会触发 malloc 图编译的模型）第一步采样就崩：

```
RuntimeError: aimdo memory compile error
  File ".../site-packages/comfy_aimdo/malloc_graph.py", line 16, in _call
    raise RuntimeError("aimdo memory compile error")
```

崩溃前一行日志通常是：

```
Comfy model compiler graph breaks: 0, rogues: N
```

根因：ComfyUI 0.37 新增的 aimdo malloc 图在该模型 / patch 组合下 C 侧编译失败。
官方绕过方式就是启动加 `--disable-comfy-compiler`。本插件在 custom-node 导入阶段
强制打开这个开关，**无需修改启动 `.bat`**，装完即生效。

### 安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/xm6018924/BSAI-ComfyUI-AimDo-Fix.git
```

重启 ComfyUI。工作流不用改任何东西。

### 它做了什么

不注册任何工作流节点。导入时依次翻转三个内部开关（幂等，每一层都有 try/except）：

1. `comfy.cli_args.args.disable_comfy_compiler = True`
2. `comfy.memory_management.aimdo_enabled = False`
3. `comfy.model_prefetch.malloc_graph_enabled = lambda device: False`

成功后控制台会打印一行：

```
[BSAI-AimDo-Fix] comfy compiler / aimdo malloc graph disabled at runtime (...).
Equivalent to --disable-comfy-compiler.
```

### 环境要求

- ComfyUI 0.37.x（存在 `comfy_aimdo` 的版本）。旧版本上是无害 no-op（只打 warning 不影响启动）。
- 不需要额外 pip 依赖。

### 说明

- 本插件**不降低画质、不改变采样结果**，只是关掉一个在该环境下编译失败的实验性内存图。
- 如果你能改启动 `.bat`，直接加 `--disable-comfy-compiler` 效果一样；本插件是为不方便改 bat 的机器准备的分发方案。
