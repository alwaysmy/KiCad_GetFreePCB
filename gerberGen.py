import wx
import pcbnew  
import os

def generate_gerber_files(board, output_dir):
    """生成 Gerber 文件"""
    # 获取当前启用的层
    enabled_layers = board.GetEnabledLayers()  # 返回 LSET 对象
    layer_ids = enabled_layers.Seq()  # 获取启用层的 ID 列表

    # 配置 Gerber 导出选项
    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()

    plot_options.SetOutputDirectory(output_dir)
    plot_options.SetPlotFrameRef(False)  # 不绘制边框 通常情况下，PCB 的边框已经通过专门的层（如 Edge.Cuts 层）导出，因此不需要额外绘制边框
    plot_options.SetPlotValue(False)      # 不绘制元件值
    plot_options.SetPlotReference(True)  # 绘制参考标识（位号）
    plot_options.SetSketchPadLineWidth(pcbnew.FromMM(0.1))  # 设置线宽
    plot_options.SetAutoScale(False)                       # 不自动缩放
    plot_options.SetScale(1)                               # 保持 1:1 比例
    plot_options.SetMirror(False)                          # 不镜像
    plot_options.SetUseGerberAttributes(True)              # 使用扩展属性
    plot_options.SetUseGerberProtelExtensions(True)        # 使用 Protel 风格扩展名
    plot_options.SetUseAuxOrigin(True)                     # 使用辅助原点
    plot_options.SetSubtractMaskFromSilk(False)            # 不从丝印中减去阻焊（厂商会处理的）
    plot_options.SetUseGerberX2format(False)               # 不使用 Gerber X2 格式
    plot_options.SetDrillMarksType(0)                      # 不显示钻孔标记

    # if hasattr(plot_options, "SetExcludeEdgeLayer"):
    #     plot_options.SetExcludeEdgeLayer(True)
    # 遍历所有启用的层并导出 Gerber 文件
    for layer_id in layer_ids:
        layer_name = board.GetLayerName(layer_id)  # 获取层名称
        print(f"正在导出层: {layer_name} (ID: {layer_id})")

        plot_controller.SetLayer(layer_id)
        plot_controller.OpenPlotfile(layer_name, pcbnew.PLOT_FORMAT_GERBER, "Gerber")
        plot_controller.PlotLayer()
        plot_controller.ClosePlot()
def generate_drill_files(board, output_dir):
    """生成钻孔文件"""
    # 创建 Excellon Writer
    drill_writer = pcbnew.EXCELLON_WRITER(board)

    # 配置钻孔文件选项
    drill_writer.SetOptions(
        aMirror=False,                  # 不镜像
        aMinimalHeader=False,          # 包含完整头部信息
        aOffset=board.GetDesignSettings().GetAuxOrigin(),        # 偏移量为 (0, 0)
        aMerge_PTH_NPTH=False           # 合并 PTH 和 NPTH 钻孔
    )

    # 设置钻孔单位为毫米
    drill_writer.SetFormat(True) #使用公制单位
    # drill_writer.SetFormat(
    #     aMetric=True,                  # 使用公制单位
    #     aZerosFmt=pcbnew.EXCELLON_WRITER.DECIMAL_FORMAT,  # 小数格式
    #     aLeftDigits=3,                 # 整数部分位数
    #     aRightDigits=3                 # 小数部分位数
    # )
    drill_writer.SetMapFileFormat(pcbnew.PLOT_FORMAT_GERBER) # 设置钻孔映射文件格式为 Gerber
    # 生成钻孔文件和映射文件
    drill_writer.CreateDrillandMapFilesSet(output_dir, True, True)  # 参数：True 表示生成钻孔文件，True 表示生成映射文件
    # print(f"钻孔文件已生成，保存在目录: {output_dir}")