# 测试工具说明

本目录包含用于测试小红书MCP工具包的测试脚本，特别是验证浏览器可视化模式。

## 测试文件

### 1. test_publish_visual.py
直接测试发布流程的可视化效果：
- 创建测试图片
- 模拟发布流程
- **不会实际发布内容**
- 验证浏览器是否以可视化模式运行

运行方法：
```bash
python tests/test_publish_visual.py
```

### 2. test_mcp_publish.py
通过MCP API接口测试发布功能：
- 测试MCP服务器连接
- 测试登录功能
- 模拟发布流程
- 验证浏览器可视化模式

运行方法：
```bash
python tests/test_mcp_publish.py
```

## 前置条件

1. **环境变量设置**
   确保在 `env` 文件中设置：
   ```
   HEADLESS=false  # 显示浏览器界面
   ```

2. **已登录状态**
   需要先执行登录获取有效的cookies：
   ```bash
   python -m src.main login
   ```

## 测试流程

1. **验证可视化模式**
   - 脚本启动后会打开Chrome浏览器
   - 你应该能看到浏览器窗口和操作过程
   - 如果浏览器在后台运行，说明无头模式未正确关闭

2. **模拟发布**
   - 脚本会模拟填写标题、内容、话题等
   - **重要**：不会点击最终的发布按钮
   - 测试完成后自动关闭浏览器

3. **查看结果**
   - 测试结果保存在 `tests/` 目录下：
     - `test_result.json` - 直接测试结果
     - `mcp_test_result.json` - MCP API测试结果
     - `test_images/` - 测试用图片

## 注意事项

⚠️ **安全提醒**：
- 这些测试脚本**不会实际发布**任何内容到小红书
- 仅用于验证浏览器可视化功能是否正常工作
- 测试过程中会打开浏览器，请勿手动点击发布按钮

## 故障排查

如果浏览器仍在后台运行（看不到窗口）：

1. 检查环境变量：
   ```bash
   grep HEADLESS env
   # 应该显示: HEADLESS=false
   ```

2. 检查代码配置：
   - `src/core/config.py` 第72行应为：`os.getenv("HEADLESS", "false")`
   - `src/server/mcp_server.py` 第825行应被注释

3. 重启MCP服务后再测试