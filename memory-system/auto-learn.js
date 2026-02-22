/**
 * Auto-Learn Module
 * Automatically extracts preferences from conversations
 */

const fs = require('fs');
const path = require('path');
const core = require('./core');

const STORAGE_PATH = '/root/.openclaw/workspace/memory-system';
const PROFILE_FILE = path.join(STORAGE_PATH, 'profile.json');

// Patterns for preference extraction
const PATTERNS = {
  // Direct preference statements
  like: /(?:我|本人)(?:喜欢|爱|偏好)([^\。\，]+)/gi,
  dislike: /(?:不喜欢|讨厌|恨|不想|不希望|别)([^\。\，]+)/gi,
  
  // Style/tone preferences
  tone: /(?:语气?|风格?|说话|回复|表达)(?:要|应该|最好|可以)?(.+?)(?:，|,|。|\.|$)/gi,
  
  // Time/preference patterns
  usually: /(?:我|通常|一般|习惯)(?:总是|经常|通常|往往|习惯)(.+?)(?:，|,|。|\.|$)/gi,
  never: /(?:我从不|我从不?会|我永远不|我不会)(.+?)(?:，|,|。|\.|$)/gi,
  
  // Goal/intent statements (more specific)
  want: /(?:我的目标|我想要?达到|我需要实现?|我计划|我想完成)(.+?)(?:，|,|。|\.|$)/gi,
  
  // Communication preferences
  brief: /(?:简洁?|简短?|精炼?|直接|少说|别啰嗦|别冗余)(?:一点|一些|地)?(?:回复|说话|表达|写)?(?:点|一些)?(?:。|\.|$)/gi,
  detailed: /(?:详细?|展开|多说|具体|全面)(?:一点|一些)?(?:解释|说明|描述)?(?:。|\.|$)/gi,
  
  // Frequency/cadence
  often: /(?:经常|时常|总是|每次|每次都)(.+?)(?:，|,|。|\.|$)/gi
};

// Extract preferences from text
function extractFromText(text) {
  const extracted = {
    likes: [],
    dislikes: [],
    habits: [],
    goals: [],
    tonePrefs: [],
    stylePrefs: []
  };
  
  // Extract likes
  let match;
  while ((match = PATTERNS.like.exec(text)) !== null) {
    const val = match[1]?.trim();
    if (val && val.length > 1 && val.length < 100) {
      extracted.likes.push(val);
    }
  }
  
  // Reset regex
  PATTERNS.like.lastIndex = 0;
  
  // Extract dislikes
  while ((match = PATTERNS.dislike.exec(text)) !== null) {
    const val = match[1]?.trim();
    if (val && val.length > 1 && val.length < 100) {
      extracted.dislikes.push(val);
    }
  }
  
  // Reset
  PATTERNS.dislike.lastIndex = 0;
  
  // Extract habits
  while ((match = PATTERNS.usually.exec(text)) !== null) {
    const val = match[1]?.trim();
    if (val && val.length > 2 && val.length < 100) {
      extracted.habits.push(val);
    }
  }
  
  // Extract goals
  while ((match = PATTERNS.want.exec(text)) !== null) {
    const val = match[1]?.trim();
    if (val && val.length > 2 && val.length < 100) {
      extracted.goals.push(val);
    }
  }
  
  // Check style preferences
  if (PATTERNS.brief.test(text)) extracted.stylePrefs.push('brief');
  if (PATTERNS.detailed.test(text)) extracted.stylePrefs.push('detailed');
  
  return extracted;
}

// Analyze a conversation and learn
function analyzeConversation(messages) {
  const text = messages
    .map(m => m.content || m.text || '')
    .join(' ');
  
  const extracted = extractFromText(text);
  
  // Get current profile
  const profile = JSON.parse(fs.readFileSync(PROFILE_FILE, 'utf8'));
  
  // Update extracted data
  const learned = {
    extractedAt: new Date().toISOString(),
    likes: extracted.likes,
    dislikes: extracted.dislikes,
    habits: extracted.habits,
    goals: extracted.goals,
    stylePrefs: extracted.stylePrefs
  };
  
  // Merge with existing learned data
  profile.learned = profile.learned || [];
  profile.learned.push(learned);
  
  // Update aggregated preferences
  profile.preferences = profile.preferences || {};
  profile.preferences.likes = [...new Set([
    ...(profile.preferences.likes || []),
    ...extracted.likes
  ])];
  profile.preferences.dislikes = [...new Set([
    ...(profile.preferences.dislikes || []),
    ...extracted.dislikes
  ])];
  profile.preferences.habits = [...new Set([
    ...(profile.preferences.habits || []),
    ...extracted.habits
  ])];
  
  fs.writeFileSync(PROFILE_FILE, JSON.stringify(profile, null, 2));
  
  return {
    extracted,
    profileUpdated: true
  };
}

// Smart suggestion based on learned patterns
function suggest(message) {
  const profile = JSON.parse(fs.readFileSync(PROFILE_FILE, 'utf8'));
  const prefs = profile.preferences || {};
  
  const suggestions = [];
  
  // Check if user likes detailed responses
  if (prefs.likes?.some(l => l.includes('详细') || l.includes('全面'))) {
    suggestions.push('detailed');
  }
  
  // Check if user prefers brief
  if (prefs.dislikes?.some(d => d.includes('啰嗦') || d.includes('冗长')) ||
      prefs.likes?.some(l => l.includes('简洁') || l.includes('简短'))) {
    suggestions.push('brief');
  }
  
  return suggestions;
}

// Run auto-learning on a message
function learn(message) {
  const result = analyzeConversation([{ content: message }]);
  return result;
}

// Batch learn from conversation history
function learnFromHistory(channel = 'mattermost') {
  const history = core.getConversationHistory(50);
  const mattermostConvs = history.filter(c => c.channel === channel);
  
  let totalExtracted = 0;
  for (const conv of mattermostConvs) {
    const result = analyzeConversation(conv.messages || []);
    totalExtracted += result.extracted.likes.length + result.extracted.dislikes.length;
  }
  
  return { conversationsProcessed: mattermostConvs.length, totalExtracted };
}

// Get learning stats
function stats() {
  try {
    const profile = JSON.parse(fs.readFileSync(PROFILE_FILE, 'utf8'));
    const learned = profile.learned || [];
    const prefs = profile.preferences || {};
    
    return {
      sessionsLearned: learned.length,
      totalLikes: (prefs.likes || []).length,
      totalDislikes: (prefs.dislikes || []).length,
      totalHabits: (prefs.habits || []).length,
      lastLearned: learned[learned.length - 1]?.extractedAt || null
    };
  } catch (e) {
    return { error: e.message };
  }
}

module.exports = {
  extractFromText,
  analyzeConversation,
  learn,
  learnFromHistory,
  suggest,
  stats
};
