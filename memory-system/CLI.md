# Auto-Learn CLI

Auto-learn 模块自动从对话中提取用户偏好。

## Usage

```javascript
const learn = require('/root/.openclaw/workspace/memory-system/auto-learn.js');

// 从单条消息学习
learn.learn("我喜欢简洁的回复");

// 从历史记录学习
learn.learnFromHistory('mattermost');

// 获取学习统计
console.log(learn.stats());

// 根据偏好给出建议
const suggestions = learn.suggest("请帮我写代码");
console.log(suggestions); // ['brief'] 如果用户喜欢简洁
```

## CLI Tool

```bash
node auto-learn.js stats        # 查看学习统计
node auto-learn.js learn "message"  # 从消息学习
node auto-learn.js history      # 从所有历史学习
node auto-learn.js suggest "msg" # 获取建议
```

## 自动触发

在主会话中，每次有效对话后会自动调用 `learn()` 提取偏好。
