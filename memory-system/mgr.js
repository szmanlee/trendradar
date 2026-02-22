#!/usr/bin/env node
/**
 * Memory System Manager CLI
 */

const fs = require('fs');
const path = require('path');
const core = require('./core');

const STORAGE_PATH = '/root/.openclaw/workspace/memory-system';
const MEMORY_FILE = STORAGE_PATH + '/memory.json';

const CMD = process.argv[2];

function help() {
  console.log(`
Memory System Manager v1.0
=========================
Usage: node mgr.js <command>

Commands:
  init        Initialize memory system
  remember    Add memory: remember <key> <value> [category]
  recall      Get memory: recall <key>
  search      Search memories: search <query>
  profile     Show user profile
  update      Update profile: update <json>
  history     Show conversation history
  backup      Create backup
  stats       Show statistics
`);
}

async function main() {
  core.init();
  
  switch(CMD) {
    case 'init':
      console.log('✓ Memory system initialized');
      break;
      
    case 'remember':
      const key = process.argv[3];
      const val = process.argv[4];
      const cat = process.argv[5] || 'general';
      if (key && val) {
        core.remember(key, val, cat);
        console.log(`✓ Remembered: ${key}`);
      } else console.log('Usage: remember <key> <value> [category]');
      break;
      
    case 'recall':
      const result = core.recall(process.argv[3]);
      console.log(result || '(not found)');
      break;
      
    case 'search':
      const results = core.search(process.argv[3] || '');
      console.log(JSON.stringify(results, null, 2));
      break;
      
    case 'profile':
      console.log(JSON.stringify(core.getProfile(), null, 2));
      break;
      
    case 'update':
      const data = JSON.parse(process.argv[3] || '{}');
      console.log(JSON.stringify(core.updateProfile('user', data), null, 2));
      break;
      
    case 'history':
      console.log(JSON.stringify(core.getConversationHistory(20), null, 2));
      break;
      
    case 'backup':
      const backupPath = path.join(path.dirname(core.STORAGE_PATH || __dirname), 'memory-backup.zip');
      console.log('✓ Backup feature (placeholder)');
      break;
      
    case 'stats':
      const profile = core.getProfile();
      const history = core.getConversationHistory(100);
      console.log({
        entries: (JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8')).entries || []).length,
        conversations: history.length,
        profileFields: Object.keys(profile.user || {}).length
      });
      break;
      
    default:
      help();
  }
}

main().catch(console.error);
