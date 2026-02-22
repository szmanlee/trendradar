/**
 * Jarvis Mode - Proactive Assistant Framework
 */

const core = require('./core');

// Jarvis Mode Configuration
const JARVIS_CONFIG = {
  mode: 'jarvis',
  tone: {
    professional: true,
    warm: true,
    concise: true,
    proactive: true
  },
  features: {
    autoSummary: true,      // Auto-summarize progress
    proactiveTips: true,    // Proactive suggestions
    taskOptimization: true, // Optimize workflows
    reminder: true          // Active reminders
  },
  style: {
    noRedundancy: true,     // No filler words
    highExecution: true,    // High执行力
    initPhrase: 'Jarvis Mode Activated'
  }
};

// Proactive suggestions based on context
function proactiveSuggest(context) {
  const profile = core.getProfile();
  const suggestions = [];
  
  // Time-based suggestions
  const hour = new Date().getHours();
  if (hour >= 23 || hour < 7) {
    suggestions.push({ type: 'reminder', text: '夜深了，建议休息' });
  }
  
  // Task-based suggestions
  if (context?.includes('coding') || context?.includes('代码')) {
    suggestions.push({ type: 'tip', text: '需要我帮你优化代码结构吗？' });
  }
  
  // Memory-based suggestions
  const learned = profile.preferences || {};
  if (learned.likes?.length > 0) {
    suggestions.push({ type: 'ack', text: `我记得你喜欢${learned.likes[learned.likes.length-1]}` });
  }
  
  return suggestions;
}

// Auto-summary generator
function summarize(sessionHistory) {
  if (!sessionHistory || sessionHistory.length === 0) return null;
  
  const lastMsg = sessionHistory[sessionHistory.length - 1];
  const summary = {
    timestamp: new Date().toISOString(),
    lastAction: lastMsg?.content?.substring(0, 50) || 'N/A',
    status: 'active',
    suggestions: proactiveSuggest(lastMsg?.content)
  };
  
  return summary;
}

// Get Jarvis greeting
function greeting() {
  return {
    text: 'Jarvis Mode Activated',
    subtext: 'Ready for your command',
    timestamp: new Date().toISOString()
  };
}

// Format response in Jarvis style
function formatResponse(content, options = {}) {
  const { brief = true, withEmoji = false } = options;
  
  // Jarvis-style: no filler, direct, professional
  let formatted = content;
  
  // Remove common filler words
  const fillers = ['好的', '没问题', '当然可以', '我来帮您', '让我看看'];
  fillers.forEach(f => {
    formatted = formatted.replace(new RegExp(f + '[，,]?', 'g'), '');
  });
  
  // Clean up spacing
  formatted = formatted.replace(/\s+/g, ' ').trim();
  
  return withEmoji ? `🤖 ${formatted}` : formatted;
}

// Export
module.exports = {
  config: JARVIS_CONFIG,
  proactiveSuggest,
  summarize,
  greeting,
  formatResponse
};
