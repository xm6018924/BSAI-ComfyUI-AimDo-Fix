# BSAI-ComfyUI-AimDo-Fix

ComfyUI 0.37.x 启动兼容补丁：运行时禁用 `comfy_aimdo` 内存图编译器，
等价于启动参数 `--disable-comfy-compiler`。

## 解决的问题

在 `--cuda-malloc` 开启、但没有加 `--disable-comfy-compiler` 的机器上，
跑 Qwen Image 2.1（以及其他会触发 malloc graph 编译的模型）第一步采样就崩：

```
RuntimeError: aimdo memory compile error
  File ".../comfy_aimdo/malloc_graph.py", line 16, in _call
    raise RuntimeError("aimdo memory compile error")
```

原因是 ComfyUI 0.37 新增的 aimdo malloc 图在该模型 / patch 组合下 C 侧编译失败。
官方绕过方式就是加 `--disable-comfy-compiler`。本插件在 custom-node 导入阶段
强制打开这个开关，无需修改启动 `.bat`。

## 安装

把整个目录放进 ComfyUI 的 `custom_nodes/`，重启 ComfyUI 即可。

## 它做了什么

不注册任何工作流节点。导入时依次：

1. `comfy.cli_args.args.disable_comfy_compiler = True`
2. `comfy.memory_management.aimdo_enabled = False`
3. `comfy.model_prefetch.malloc_graph_enabled = lambda device: False`

三重保险，幂等，任意一层失败不影响其它层。
