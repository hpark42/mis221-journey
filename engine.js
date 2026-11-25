// engine.js — runs the unchanged app.py inside Pyodide and turns what it prints into game data.
// app.py is never edited. Each time the player answers, app.py is replayed from the start with the
// same random seed and the full list of answers so far; input() is fed those answers and gets EOF
// (EOFError) when it asks for one the player hasn't given yet. Same seed + same answers = same game.
(function (root) {
  'use strict';

  var GAME_FILES = ['app.py', 'instr_events.txt', 'ta_events.txt', 'student_events.txt', 'quiz.txt'];

  var STAT_PATTERNS = [
    [/Dean approval: (-?[\d.]+)\t+Student satisfaction: (-?[\d.]+)\t+Colleague satisfaction: (-?[\d.]+)/,
      function (m) { return { dean: +m[1], students: +m[2], colleagues: +m[3] }; }],
    [/Instructor trust: (-?[\d.]+)\t+Student rapport: (-?[\d.]+)/,
      function (m) { return { trust: +m[1], rapport: +m[2] }; }],
    [/Current score: (-?[\d.]+)\t+Current strikes: (-?\d+)\/3/,
      function (m) { return { grade: +m[1], strikes: +m[2] }; }],
    [/^Current score: (-?[\d.]+)\s*$/, function (m) { return { grade: +m[1] }; }],
    [/^Grade: (-?[\d.]+)\t+Strikes: (-?\d+)\/3/, function (m) { return { grade: +m[1], strikes: +m[2] }; }]
  ];
  var PROMPTS = ['Your choice (a/b): ', 'Your answer (a/b/c/d): ', 'Enter your choice: '];

  function statsIn(line) {
    for (var i = 0; i < STAT_PATTERNS.length; i++) {
      var m = line.match(STAT_PATTERNS[i][0]);
      if (m) return STAT_PATTERNS[i][1](m);
    }
    return null;
  }

  function isChrome(line) {
    // lines app.py prints that are framing, not story text
    return /^===.*===$/.test(line) || /^(WIN|LOSE): /.test(line) || line === '[ FINAL REPORT ]' ||
      /^Choose your character:/.test(line) || /^\d\. /.test(line) || line === '[ MAIN MENU ]';
  }

  // Split newly printed text into: story/outcome lines, latest stats, the next question, and the ending.
  function parseSegment(seg, finished) {
    var lines = seg.split('\n');
    var question = null;
    var body = lines;
    if (!finished) {
      var last = lines[lines.length - 1];
      if (PROMPTS.indexOf(last) !== -1 && last !== 'Enter your choice: ') {
        var aIdx = -1;
        for (var i = lines.length - 2; i >= 0; i--) { if (lines[i].indexOf('a) ') === 0) { aIdx = i; break; } }
        if (aIdx > 0) {
          var choices = lines.slice(aIdx, lines.length - 1).map(function (l) { return l.slice(3); });
          question = { prompt: lines[aIdx - 1], choices: choices, kind: choices.length === 4 ? 'quiz' : 'event' };
          body = lines.slice(0, aIdx - 1);
        }
      }
    }
    var stats = {};
    var story = [];
    var ending = null, fortune = [], thanks = '';
    var inFortune = false;
    body.forEach(function (raw) {
      var line = raw.replace(/\s+$/, '');
      if (!line) return;
      if (line === "=== TODAY'S FORTUNE ===") { inFortune = true; return; }
      if (inFortune) { fortune.push(line); return; }
      var s = statsIn(line);
      if (s) { Object.assign(stats, s); return; }
      if (/VICTORY$|GAME OVER/.test(line)) { ending = line; return; }
      if (/^Thanks for playing/.test(line)) { thanks = line; return; }
      if (isChrome(line)) return;
      story.push(line);
    });
    return { question: question, stats: stats, story: story, ending: ending, fortune: fortune, thanks: thanks };
  }

  function Engine(pyodide) {
    this.py = pyodide;
    this.files = {};
    this.out = '';
    this.queue = [];
    var self = this;
    var dec = new TextDecoder();
    pyodide.setStdout({ write: function (buf) { self.out += dec.decode(buf, { stream: true }); return buf.length; } });
    pyodide.setStderr({ write: function (buf) { self.out += dec.decode(buf, { stream: true }); return buf.length; } });
    pyodide.setStdin({ stdin: function () { return self.queue.length ? self.queue.shift() : undefined; } });
  }

  Engine.prototype.load = async function (fetchText) {
    for (var i = 0; i < GAME_FILES.length; i++) {
      var name = GAME_FILES[i];
      var text = await fetchText(name);
      this.files[name] = text;
      this.py.FS.writeFile(name, text);
    }
  };

  Engine.prototype.countLines = function (name) {
    return this.files[name].split('\n').filter(function (l) { return l.trim(); }).length;
  };

  // Replays app.py from the start with the current answers; returns everything it printed.
  Engine.prototype.replay = function () {
    this.out = '';
    this.queue = this.inputs.slice();
    this.py.runPython(
      'import random, runpy\n' +
      'random.seed(' + this.seed + ')\n' +
      'try:\n' +
      "    runpy.run_path('app.py', run_name='__main__')\n" +
      '    _mis_finished = True\n' +
      'except EOFError:\n' +
      '    _mis_finished = False\n');
    return { text: this.out, finished: this.py.globals.get('_mis_finished') === true };
  };

  // menuChoice is what a player would type at app.py's main menu: "1", "2" or "3".
  Engine.prototype.newGame = function (menuChoice) {
    this.seed = Math.floor(Math.random() * 2147483647);
    this.inputs = [String(menuChoice)];
    var r = this.replay();
    var start = r.text.indexOf('Enter your choice: ') + 'Enter your choice: '.length;
    this.printed = r.text.length;
    return parseSegment(r.text.slice(start), r.finished);
  };

  // letter: "a" / "b" (events) or "a"–"d" (quiz). Returns only what app.py printed after this answer.
  Engine.prototype.answer = function (letter) {
    this.inputs.push(letter);
    var r = this.replay();
    var seg = r.text.slice(this.printed);
    this.printed = r.text.length;
    var p = parseSegment(seg, r.finished);
    p.finished = r.finished;
    return p;
  };

  root.MISEngine = { Engine: Engine, parseSegment: parseSegment, GAME_FILES: GAME_FILES };
})(typeof window !== 'undefined' ? window : globalThis);
