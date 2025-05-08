# 图片显示器 - 打包说明

## 打包前准备

1. 确保已安装以下Python包：
   - PyQt6
   - Pillow
   - PyInstaller

   可以使用以下命令安装：
   ```
   pip install PyQt6 Pillow pyinstaller
   ```

2. 确保项目目录结构如下：
   - image_display.py (主程序)
   - gxipy/ (相机SDK目录)
   - app_icon.ico (应用图标)
   - captured_images/ (拍摄照片保存目录)

## 打包方法

### 方法 1: 使用批处理文件打包

1. 执行 `package.bat` 批处理文件

### 方法 2: 手动执行 PyInstaller 命令

1. 打开命令行窗口
2. 执行以下命令：
   ```
   pyinstaller --clean 图片显示器_updated.spec
   ```

## 打包后的文件

打包完成后，生成的可执行文件将位于 `dist/图片显示器` 目录中。

## 分发应用程序

要分发应用程序，只需要将 `dist/图片显示器` 目录中的所有文件复制到目标计算机上。

### 注意事项

- 如果目标计算机上需要使用相机功能，确保已安装对应的相机驱动
- 如果运行时出现找不到 DLL 文件的错误，可能需要安装 Microsoft Visual C++ Redistributable

## 故障排除

如果打包后的应用程序无法正常运行：

1. 检查是否缺少必要的 DLL 文件
2. 检查 gxipy 目录是否被正确打包
3. 尝试在命令行中运行应用程序查看错误信息

如有问题，请联系 @RuiboLan 