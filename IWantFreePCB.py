import os
import zipfile
import shutil  
import wx
from pcbnew import *
import pcbnew
from datetime import datetime
from .file_processor import process_files, recompress_folder
# 读取header文件(专业版文件头不带个人id...不用修改)
from .gerberGen import generate_gerber_files,generate_drill_files
path = r"."
textFile="""如何进行PCB下单

请查看：
https://docs.lceda.cn/cn/PCB/Order-PCB"""
textFileName="PCB下单必读.txt"
def alert(s, icon=0):
    print(s)
    wx.MessageBox(s, '阿巴阿巴title', wx.OK|icon)
    # wx.MessageBox("功能尚未实现：直接生成 Gerber 文件", "提示", wx.OK | wx.ICON_INFORMATION)
class Dialog(wx.Dialog):  # 继承 wx.Dialog
    def __init__(self):
        super(Dialog, self).__init__(
            None,
            id=wx.ID_ANY,
            title=u"--我-要-P-C-B---",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.DEFAULT_DIALOG_STYLE
        )
    
        icon = wx.Icon(os.path.join(os.path.dirname(__file__), 'icon.png'))
        self.SetIcon(icon)
        # 设置背景颜色
        self.SetBackgroundColour(wx.LIGHT_GREY)

        # 设置窗口尺寸限制
        self.SetSizeHints(wx.Size(600, 100), wx.Size(800, 600))

        # 创建垂直布局管理器
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 添加提示文本
        text = wx.StaticText(self, label="请选择操作：")
        main_sizer.Add(text, 0, wx.ALL | wx.CENTER, 10)

        # 创建按钮：选择已有 Gerber
        btn_select_gerber = wx.Button(self, label="选择已有 Gerber")
        btn_select_gerber.Bind(wx.EVT_BUTTON, self.on_select_gerber)
        main_sizer.Add(btn_select_gerber, 0, wx.ALL | wx.EXPAND, 10)

        # 创建按钮：直接生成 Gerber
        btn_generate_gerber = wx.Button(self, label="直接生成 Gerber")
        btn_generate_gerber.Bind(wx.EVT_BUTTON, self.on_generate_gerber)
        main_sizer.Add(btn_generate_gerber, 0, wx.ALL | wx.EXPAND, 10)

        # 设置主布局
        self.SetSizer(main_sizer)
        self.Layout()

        # 将窗口居中显示
        self.Centre(wx.BOTH)

    def on_select_gerber(self, event):
        """选择已有 Gerber 文件"""
        with wx.FileDialog(
            self,
            "选择 Gerber 文件",
            wildcard="ZIP files (*.zip)|*.zip|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # 用户取消选择

            # 获取用户选择的文件路径
            zip_file = file_dialog.GetPath()
            folderpath = os.path.dirname(zip_file)
            filename = os.path.splitext(os.path.basename(zip_file))[0]
            print("文件路径：", folderpath)
            print("文件名：", filename)

            # 解压缩到临时文件夹
            temp_path = os.path.join(folderpath, filename)
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                print(f"已解压文件到：{temp_path}")
            except Exception as e:
                wx.MessageBox(f"解压失败：{e}", "错误", wx.OK | wx.ICON_ERROR)
                return

            # 处理解压后的文件
            try:
                process_files(temp_path)
            except Exception as e:
                wx.MessageBox(f"处理文件时出错：{e}", "错误", wx.OK | wx.ICON_ERROR)
                return

            # 重新压缩文件夹
            new_zip_name = os.path.join(folderpath, f"{filename}_JLC.zip")
            try:
                recompress_folder(temp_path, new_zip_name)
                wx.MessageBox(f"已生成新的压缩文件：{new_zip_name}", "成功", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"重新压缩失败：{e}", "错误", wx.OK | wx.ICON_ERROR)
                return

            # 删除临时解压的文件夹
            try:
                shutil.rmtree(temp_path)
                print(f"已删除临时文件夹：{temp_path}")
            except Exception as e:
                wx.MessageBox(f"删除临时文件夹失败：{e}", "警告", wx.OK | wx.ICON_WARNING)

    def on_generate_gerber(self, event):
        """直接生成 Gerber 文件和钻孔文件，并进行二次处理后打包为 ZIP"""
        try:
            # 获取当前 PCB 文件
            board = pcbnew.GetBoard()
            if not board:
                wx.MessageBox("未找到当前 PCB 文件", "错误", wx.OK | wx.ICON_ERROR)
                return

            # 获取 PCB 名称
            pcb_file_name = board.GetFileName()
            if not pcb_file_name:
                wx.MessageBox("无法获取当前 PCB 文件名", "错误", wx.OK | wx.ICON_ERROR)
                return
            brd_name = os.path.splitext(os.path.basename(pcb_file_name))[0]  # 提取板子名称

            # 获取当前日期
            current_date = datetime.now().strftime("%Y%m%d")  # 格式化为 YYYYMMDD

            # 配置输出目录
            output_dir = "Gerber_Output"
            os.makedirs(output_dir, exist_ok=True)  # 创建输出目录

            # 生成 Gerber 文件
            generate_gerber_files(board, output_dir)

            # 生成钻孔文件
            generate_drill_files(board, output_dir)

            # 对生成的文件进行二次处理
            try:
                process_files(output_dir)
            except Exception as e:
                wx.MessageBox(f"处理文件时出错：{e}", "错误", wx.OK | wx.ICON_ERROR)
                return

            # 动态生成 ZIP 文件名
            zip_filename = f"Gerber_{brd_name}_{current_date}_JLC.zip"
            zip_filepath = os.path.abspath(os.path.join(os.path.dirname(output_dir), zip_filename))

            # 将处理后的文件打包为 ZIP
            try:
                recompress_folder(output_dir, zip_filepath)
                # wx.MessageBox(f"Gerber 文件已生成并打包为 ZIP，保存为: {zip_filepath}", "成功", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"打包 ZIP 文件失败：{e}", "错误", wx.OK | wx.ICON_ERROR)
                return

            # 删除临时文件夹
            try:
                shutil.rmtree(output_dir)
                print(f"已删除临时文件夹：{output_dir}")
            except Exception as e:
                wx.MessageBox(f"删除临时文件夹失败：{e}", "警告", wx.OK | wx.ICON_WARNING)

        except Exception as e:
            wx.MessageBox(f"生成文件失败：{e}", "错误", wx.OK | wx.ICON_ERROR)

        # 弹出完成消息框，并提供“打开文件夹”按钮
                # 为文件路径添加双引号
        quoted_path = f'"{os.path.abspath(os.path.join(os.path.dirname(output_dir), zip_filename))}"'

        # 将文件路径复制到剪切板
        clipboard = wx.Clipboard.Get()
        if clipboard.Open():
            data = wx.TextDataObject(quoted_path)  # 设置要复制的文本
            clipboard.SetData(data)
            clipboard.Close()
            wx.MessageBox(f"文件路径已复制到剪切板：\n{quoted_path}", "成功", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("无法访问剪切板", "错误", wx.OK | wx.ICON_ERROR)
        self.show_completion_dialog(zip_filepath)

    def show_completion_dialog(self, zip_filepath):
        """显示完成消息框，并提供“打开文件夹”按钮"""
        dialog = wx.MessageDialog(
            self,
            f"Gerber 文件已生成并打包为 ZIP。\n文件路径：{zip_filepath}\n\n是否打开文件所在文件夹？",
            "处理完成",
            wx.YES_NO | wx.ICON_INFORMATION
        )
        dialog.SetYesNoLabels("打开文件夹", "取消")  # 自定义按钮标签
        result = dialog.ShowModal()
        dialog.Destroy()

        if result == wx.ID_YES:
            # 打开 ZIP 文件所在的文件夹
            folder_path = os.path.dirname(zip_filepath)
            try:
                if os.name == "nt":  # Windows
                    os.startfile(folder_path)
                elif os.name == "posix":  # macOS 或 Linux
                    import subprocess
                    subprocess.run(["open", folder_path])  # macOS
                    # subprocess.run(["xdg-open", folder_path])  # Linux
            except Exception as e:
                wx.MessageBox(f"无法打开文件夹：{e}", "错误", wx.OK | wx.ICON_ERROR)

class GiveMeFreePCB(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "马上白嫖"
        self.category = "生产制造"
        self.description = "伪装成JLCEDA的Gerber"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")
        self.show_toolbar_button = True

    # 在用户操作时执行的插件的入口函数
    def Run(self):
        # alert(textFile, wx.ICON_INFORMATION)
        myDialog = Dialog()
        myDialog.Show()