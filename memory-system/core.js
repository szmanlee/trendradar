/**
 * Local Memory System - Core Module
 * Lightweight, self-hosted memory persistence
 */

const fs = require('fs');
const path = require('path');

const STORAGE_PATH = '/root/.openclaw/workspace/memory-system';
const MEMORY_FILE = path.join(STORAGE_PATH, 'memory.json');
const PROFILE_FILE = path.join(STORAGE_PATH, 'profile.json');
const HISTORY_DIR = path.join(STORAGE_PATH, 'conversations');
const KNOWLEDGE_FILE = path.join(STORAGE_PATH, 'knowledge', 'preferences.json');

// Initialize system
function init() {
  if (!fs.existsSync(HISTORY_DIR)) fs.mkdirSync(HISTORY_DIR, { recursive: true });
  if (!fs.existsSync(path.join(STORAGE_PATH, 'knowledge'))) fs.mkdirSync(path.join(STORAGE_PATH, 'knowledge'), { recursive: true });
  
  // Ensure memory files exist
  if (!fs.existsSync(MEMORY_FILE)) fs.writeFileSync(MEMORY_FILE, JSON.stringify({ entries: [], lastUpdated: null }, null, 2));
  if (!fs.existsSync(PROFILE_FILE)) fs.writeFileSync(PROFILE_FILE, JSON.stringify({ 
    user: {}, 
    agent: {}, 
    habits: {},
    preferences: {},
    metadata: { created: new Date().toISOString(), version: '1.0.0' }
  }, null, 2));
}

// Add a memory entry
function remember(key, value, category = 'general', tags = []) {
  const memory = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
  const entry = {
    key,
    value,
    category,
    tags,
    timestamp: new Date().toISOString()
  };
  memory.entries.push(entry);
  memory.lastUpdated = new Date().toISOString();
  fs.writeFileSync(MEMORY_FILE, JSON.stringify(memory, null, 2));
  return entry;
}

// Recall a memory
function recall(key) {
  try {
    const memory = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
    const entry = memory.entries.find(e => e.key === key);
    return entry ? entry.value : null;
  } catch (e) { return null; }
}

// Search memories
function search(query) {
  try {
    const memory = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
    const q = query.toLowerCase();
    return memory.entries.filter(e => 
      e.key.toLowerCase().includes(q) || 
      e.value.toLowerCase().includes(q) ||
      e.tags.some(t => t.toLowerCase().includes(q))
    );
  } catch (e) { return []; }
}

// Update user profile
function updateProfile(user, data) {
  const profile = JSON.parse(fs.readFileSync(PROFILE_FILE, 'utf8'));
  profile.user = { ...profile.user, ...data };
  fs.writeFileSync(PROFILE_FILE, JSON.stringify(profile, null, 2));
  return profile.user;
}

// Get user profile
function getProfile() {
  try { return JSON.parse(fs.readFileSync(PROFILE_FILE, 'utf8')); } 
  catch (e) { return null; }
}

// Extract and save preferences from conversation
function learnFromConversation(messages) {
  const keywords = {
    'prefer': [], 'like': [], 'dislike': [], 'want': [], 'need': [],
    'hate': [], 'love': [], 'always': [], 'never': [], 'usually': []
  };
  
  const text = messages.map(m => m.content || '').join(' ').toLowerCase();
  
  // Simple pattern extraction (can be enhanced)
  const patterns = {
    preferences: /I (prefer|like|love|dislike|hate|want|need) (.+?)(?:\.|$)/gi,
    habits: /I (usually|always|never) (.+?)(?:\.|$)/gi
  };
  
  return { text, keywords, patterns };
}

// Record conversation
function recordConversation(channel, messages) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `conv-${channel}-${timestamp}.json`;
  const filepath = path.join(HISTORY_DIR, filename);
  
  fs.writeFileSync(filepath, JSON.stringify({
    channel,
    timestamp,
    messageCount: messages.length,
    messages
  }, null, 2));
  
  return filepath;
}

// Get conversation history
function getConversationHistory(limit = 10) {
  try {
    const files = fs.readdirSync(HISTORY_DIR)
      .filter(f => f.startsWith('conv-'))
      .sort()
      .reverse()
      .slice(0, limit);
    
    return files.map(f => {
      const content = fs.readFileSync(path.join(HISTORY_DIR, f), 'utf8');
      return JSON.parse(content);
    });
  } catch (e) { return []; }
}

// Export for external use
module.exports = {
  init,
  remember,
  recall,
  search,
  updateProfile,
  getProfile,
  learnFromConversation,
  recordConversation,
  getConversationHistory
};
