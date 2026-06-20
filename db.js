const fs = require('fs');
const path = require('path');

const CONTENT_PATH = path.join(__dirname, 'data', 'content.json');
const MESSAGES_PATH = path.join(__dirname, 'data', 'messages.json');

function readJSON(p) {
  return JSON.parse(fs.readFileSync(p, 'utf-8'));
}
function writeJSON(p, data) {
  fs.writeFileSync(p, JSON.stringify(data, null, 2), 'utf-8');
}

module.exports = {
  getContent: () => readJSON(CONTENT_PATH),
  saveContent: (data) => writeJSON(CONTENT_PATH, data),
  getMessages: () => readJSON(MESSAGES_PATH),
  addMessage: (msg) => {
    const list = readJSON(MESSAGES_PATH);
    list.unshift({ ...msg, id: Date.now(), date: new Date().toISOString() });
    writeJSON(MESSAGES_PATH, list);
  },
  deleteMessage: (id) => {
    const list = readJSON(MESSAGES_PATH).filter(m => String(m.id) !== String(id));
    writeJSON(MESSAGES_PATH, list);
  }
};
