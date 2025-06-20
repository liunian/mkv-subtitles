# MKV 字幕提取

## 调试

```bash
# 生成构建配置文件
cmake . -B build

# 构建
cmake --build build -j 8
```

## 发布

```bash
# 生成构建配置文件
cmake . -B build

# 构建
cmake --build build --config Release -j 8
```

### 生成安装包

> 还有些问题，比如需要手动运行 xxdeployqt，甚至运行后，cpack 打包出来的文件还是缺少 qt 运行库
> 可以先手动将 Release 做成压缩包

```bash
# 安装（收集可执行和资源）
cmake --install build --prefix build/install --config Release

# 用 windeployqt/macdeployqt 将依赖 DLL 拷贝进 install
windeployqt build/install/MyQtApp.exe

# 打包（生成 .exe / .dmg / .deb 等）
cpack --config build/CPackConfig.cmake -C Release
```