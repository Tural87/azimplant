// Usage: node scripts/hash-password.js yourPassword
const bcrypt = require('bcryptjs');
const pwd = process.argv[2];
if (!pwd) {
  console.log('Usage: node scripts/hash-password.js yourPassword');
  process.exit(1);
}
const hash = bcrypt.hashSync(pwd, 10);
console.log('\nADMIN_PASS_HASH=' + hash + '\n');
console.log('Bunu .env faylına yapışdırın.');
