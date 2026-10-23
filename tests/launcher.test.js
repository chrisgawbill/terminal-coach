const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const test = require('node:test');

const launcher = path.resolve(__dirname, '../bin/terminalCoach');

function run(cwd, env) {
  return spawnSync(process.execPath, [launcher, ...env.args], {
    cwd,
    env: { ...process.env, ...env },
    encoding: 'utf8',
  });
}

test('forwards cwd and arguments, adds the package to PYTHONPATH, and returns Python status', (t) => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'terminal-coach-launcher-'));
  t.after(() => fs.rmSync(temp, { recursive: true, force: true }));
  const fakeBin = path.join(temp, 'bin');
  fs.mkdirSync(fakeBin);
  const capture = path.join(temp, 'capture.json');
  const python = path.join(fakeBin, 'python3');
  fs.writeFileSync(python, `#!${process.execPath}\nconst fs = require('node:fs');\nfs.writeFileSync(process.env.CAPTURE, JSON.stringify({ cwd: process.cwd(), args: process.argv.slice(2), pythonpath: process.env.PYTHONPATH }));\nprocess.exit(Number(process.env.CHILD_STATUS));\n`);
  fs.chmodSync(python, 0o755);
  const cwd = path.join(temp, 'working directory');
  fs.mkdirSync(cwd);
  const result = run(cwd, {
    args: ['--help', 'some value'],
    PATH: fakeBin,
    CAPTURE: capture,
    CHILD_STATUS: '37',
    PYTHONPATH: '/existing/python/path',
  });

  assert.equal(result.status, 37);
  assert.deepEqual(JSON.parse(fs.readFileSync(capture, 'utf8')), {
    cwd,
    args: ['-m', 'terminal_coach', '--help', 'some value'],
    pythonpath: `${path.resolve(__dirname, '..')}:/existing/python/path`,
  });
});

test('reports a missing Python interpreter cleanly', (t) => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'terminal-coach-no-python-'));
  t.after(() => fs.rmSync(temp, { recursive: true, force: true }));
  const result = run(temp, { args: ['--help'], PATH: temp });

  assert.equal(result.status, 1);
  assert.match(result.stderr, /requires Python 3\.10 or newer \(python3 was not found\)/);
});
