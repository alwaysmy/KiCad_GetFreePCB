import os
import zipfile
import shutil


def process_files(path):
    """处理解压后的文件"""
    # 读取 header 文件
    # 获取 headerPro.txt 的绝对路径
    header_file_path = os.path.join(os.path.dirname(__file__), 'headerPro.txt')
    try:
        with open(header_file_path, 'r') as f:
            header = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"未找到 headerPro.txt 文件，请确保文件位于 {os.path.dirname(__file__)} 目录下")

    # 遍历文件并重命名
    current_dir = os.listdir(path)
    for file in current_dir:
        if os.path.splitext(file)[-1][1:].lower() == "gbl":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_BottomLayer.GBL"))
        elif os.path.splitext(file)[-1][1:].lower() == "gko":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_BoardOutlineLayer.GKO"))
        elif os.path.splitext(file)[-1][1:].lower() == "gbp":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_BottomPasteMaskLayer.GBP"))
        elif os.path.splitext(file)[-1][1:].lower() == "gbo":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_BottomSilkscreenLayer.GBO"))
        elif os.path.splitext(file)[-1][1:].lower() == "gbs":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_BottomSolderMaskLayer.GBS"))
        elif os.path.splitext(file)[-1][1:].lower() == "gtl":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_TopLayer.GTL"))
        elif os.path.splitext(file)[-1][1:].lower() == "gtp":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_TopPasteMaskLayer.GTP"))
        elif os.path.splitext(file)[-1][1:].lower() == "gto":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_TopSilkscreenLayer.GTO"))
        elif os.path.splitext(file)[-1][1:].lower() == "gts":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_TopSolderMaskLayer.GTS"))
        elif os.path.splitext(file)[-1][1:].lower() == "gd1":
            os.rename(os.path.join(path, file), os.path.join(path, "Drill_Through.GD1"))
        elif os.path.splitext(file)[-1][1:].lower() == "gm1":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_MechanicalLayer1.GM1"))
        elif os.path.splitext(file)[-1][1:].lower() == "gm13":
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_MechanicalLayer13.GM13"))

        # 这部分似乎不修改名称也没事。。。所以内层更多我就懒得修改处理方法了。。。
        if "-PTH.drl" in file:
            os.rename(os.path.join(path, file), os.path.join(path, "Drill_PTH_Through.DRL"))
        elif "-NPTH.drl" in file:
            os.rename(os.path.join(path, file), os.path.join(path, "Drill_NPTH_Through.DRL"))
        elif "-In1_Cu" in file or ".G1" in file:
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_InnerLayer1.G1"))
        elif "-In2_Cu" in file or ".G2" in file:
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_InnerLayer2.G2"))
        elif "-In3_Cu" in file or ".G3" in file:
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_InnerLayer3.G3"))
        elif "-In4_Cu" in file or ".G4" in file:
            os.rename(os.path.join(path, file), os.path.join(path, "Gerber_InnerLayer4.G4"))
        # 由于KiCad外形导出为xxx-Edge_Cuts.gm1，前面已经修改了，这里就不用改一次了，否则会报错，
        # 因为文件已经不存在，由于我发现.GKO可以不要，所以也不复制一份了。
        # elif "-Edge_Cuts" in file:
        #     os.rename(os.path.join(path, file), os.path.join(path, "Gerber_BoardOutlineLayer.GKO"))

    # 修改文件内容
    current_dir = os.listdir(path)
    for file in current_dir:
        file_type = os.path.splitext(file)[-1][1:].lower()
        if file_type not in ["txt", "py"]:
            file_path = os.path.join(path, file)
            with open(file_path, "r") as f:
                file_data = f.read()
            with open(file_path, "w") as f:
                f.write(header)
                f.write(file_data)

    # 创建 PCB 下单必读文件
    text_file_content = """如何进行PCB下单

请查看：
https://docs.lceda.cn/cn/PCB/Order-PCB"""
    text_file_path = os.path.join(path, "PCB下单必读.txt")
    with open(text_file_path, "w") as f:
        f.write(text_file_content)


def recompress_folder(folder_path, output_zip):
    """重新压缩文件夹"""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root_dir, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root_dir, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)