"""Human guidance on stderr only; no input payloads or exception values echoed."""
import sys
from pathlib import Path

PDF_INSTALL = 'python -m pip install ".[pdf]"'

def utf8_console():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

def failure(error, output=None):
    if isinstance(error, FileExistsError) or (output is not None and Path(output).exists()):
        reason = "输出文件或目录已存在。请换一个新名字；旧输出未覆盖。"
    elif isinstance(error, ImportError):
        reason = "缺少可选PDF读取组件。在本仓目录中运行 " + PDF_INSTALL + " 后重试（安装需联网或本地依赖源）。"
    elif isinstance(error, FileNotFoundError):
        reason = "输入文件或本地原文不存在。请核对输入路径、相对路径所在目录及原文文件。"
    elif isinstance(error, OSError):
        reason = "文件读写失败。请检查路径、目录权限和可用空间；不要覆盖旧输出。"
    else:
        # Domain ValueError messages are authored by this package; JSON and key/type
        # errors may include caller supplied data, so never echo their exception text.
        hints = (
            "事实披露晚于截止日", "经营指标期间或更正版本不同",
            "指标语义冲突", "事实字段未知", "未知输入schema",
            "方法版本不支持", "原文文件摘要不一致或文件缺失",
            "首版只核对明确金额单位", "PDF物理页码须为正整数",
        )
        detail = next((hint for hint in hints if hint in str(error)), "输入或口径无效")
        reason = detail + "。请按README及对应接口说明核对schema、字段、金额单位、日期、版本和证据；旧输出未覆盖。"
    return "未能完成：" + reason + "\n"

def saved(action, output, open_file=None, teaching=False):
    label = "输入声明为教学样本，未核真实原文。" if teaching else "按选定输入生成，不代表原文认证或完整验收。"
    text = action + "完成；" + label + "结果位置：" + str(Path(output).resolve()) + "。"
    if open_file is not None:
        text += "打开：" + str(Path(open_file).resolve()) + "。"
    print(text, file=sys.stderr)

def pdf_unavailable():
    print("原页未核验：缺少可选PDF组件。需要原页检查时，在本仓目录运行 " + PDF_INSTALL + "；安装需联网或本地依赖源。", file=sys.stderr)
