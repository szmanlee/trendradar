# Local Memory System

Lightweight, self-hosted persistent memory for OpenClaw.

## Features

- **Remember** - Store key-value memories with categories and tags
- **Recall** - Retrieve stored memories by key
- **Search** - Full-text search across all memories
- **Profile** - Track user preferences and habits
- **History** - Store conversation history locally

## Usage

```javascript
const memory = require('/root/.openclaw/workspace/memory-system/core.js');

// Initialize
memory.init();

// Remember something
memory.remember('user_timezone', 'UTC', 'preference', ['timezone', 'user']);

// Recall
const tz = memory.recall('user_timezone'); // returns 'UTC'

// Update user profile
memory.updateProfile('user', {
  name: 'szmanlee',
  preferences: {
    language: 'Chinese',
    tone: 'professional'
  }
});

// Record a conversation
memory.recordConversation('mattermost', messages);

// Get conversation history
const history = memory.getConversationHistory(10);
```

## CLI Tools

```bash
cd /root/.openclaw/workspace/memory-system
node mgr.js remember <key> <value> [category]
node mgr.js recall <key>
node mgr.js search <query>
node mgr.js profile
node mgr.js history
node mgr.js stats
```

## Files

- `core.js` - Core memory functions
- `mgr.js` - CLI manager
- `memory.json` - Stored memories
- `profile.json` - User profile
- `conversations/` - Conversation history
