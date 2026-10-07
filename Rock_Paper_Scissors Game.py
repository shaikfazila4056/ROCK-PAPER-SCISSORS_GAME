from flask import Flask, render_template_string, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = "ultimate_rps_pro_key"

CHOICES = ["rock", "paper", "scissors"]

BEATS = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper"
}

ACTION_VERBS = {
    ("rock", "scissors"): "crushes",
    ("paper", "rock"): "covers",
    ("scissors", "paper"): "cuts"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rock Paper Scissors Pro Edition</title>
    <!-- Canvas Confetti Library -->
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --bg-dark: #0f172a;
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --win: #10b981;
            --lose: #ef4444;
            --tie: #f59e0b;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }

        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1.5rem;
            color: var(--text-main);
            background: linear-gradient(-45deg, #0f172a, #1e1b4b, #311042, #022c22);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 2rem;
            max-width: 580px;
            width: 100%;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            text-align: center;
        }

        /* Username Header */
        .user-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(15, 23, 42, 0.6);
            padding: 0.75rem 1.25rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--glass-border);
        }

        .user-info { display: flex; align-items: center; gap: 8px; font-weight: 600; }
        .edit-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.85rem;
            text-decoration: underline;
        }
        .edit-btn:hover { color: var(--text-main); }

        h1 { font-size: 2rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 0.25rem; }

        /* Mode & Sound controls */
        .settings-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        select {
            background: #0f172a;
            color: var(--text-main);
            border: 1px solid var(--glass-border);
            padding: 6px 12px;
            border-radius: 8px;
            outline: none;
            cursor: pointer;
        }

        /* Scoreboard Grid */
        .scoreboard {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            background: rgba(15, 23, 42, 0.6);
            padding: 1rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--glass-border);
        }

        .stat-box { text-align: center; }
        .stat-val { font-size: 1.5rem; font-weight: 700; }
        .stat-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

        /* Battle Arena */
        .arena {
            display: flex;
            justify-content: space-around;
            align-items: center;
            background: rgba(15, 23, 42, 0.4);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--glass-border);
        }

        .fighter { display: flex; flex-direction: column; align-items: center; gap: 8px; }
        .fighter-name { font-size: 0.85rem; color: var(--text-muted); font-weight: 600; }
        .choice-icon {
            font-size: 3.5rem;
            transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .bounce { animation: bounce 0.4s ease; }
        @keyframes bounce {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.3); }
        }

        .vs-badge {
            background: var(--primary);
            color: white;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
        }

        /* Results Display */
        .result-box { min-height: 60px; margin-bottom: 1.5rem; }
        .result-title { font-size: 1.3rem; font-weight: 700; margin-bottom: 4px; }
        .result-sub { font-size: 0.85rem; color: var(--text-muted); }

        /* Weapon Selection Buttons */
        .weapon-buttons {
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-bottom: 1.5rem;
        }

        .btn-weapon {
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid var(--glass-border);
            border-radius: 50%;
            width: 80px;
            height: 80px;
            font-size: 2.2rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .btn-weapon:hover {
            background: var(--primary);
            border-color: var(--primary-hover);
            transform: translateY(-6px) scale(1.05);
            box-shadow: 0 10px 20px rgba(99, 102, 241, 0.4);
        }

        .btn-action {
            background: transparent;
            border: 1px solid var(--glass-border);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }
        .btn-action:hover { background: rgba(255, 255, 255, 0.1); color: var(--text-main); }

        /* Username Modal */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 100;
        }

        .modal-card {
            background: var(--bg-dark);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 2rem;
            max-width: 380px;
            width: 90%;
            text-align: center;
        }

        .modal-card input {
            width: 100%;
            padding: 10px 14px;
            margin: 1rem 0;
            background: #1e293b;
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            outline: none;
        }

        .modal-card button {
            width: 100%;
            padding: 10px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>

    <!-- Username Prompt Modal -->
    <div class="modal-overlay" id="userModal" style="display: none;">
        <div class="modal-card">
            <h2>Welcome Fighter!</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 4px;">Enter your username to begin tracking stats.</p>
            <input type="text" id="usernameInput" placeholder="Enter Player Name..." maxlength="15">
            <button onclick="saveUsername()">Start Playing</button>
        </div>
    </div>

    <div class="glass-card">
        <!-- Player Info Bar -->
        <div class="user-bar">
            <div class="user-info">
                <span>👤</span>
                <span id="displayUsername">Player</span>
            </div>
            <button class="edit-btn" onclick="openUserModal()">Change Name</button>
        </div>

        <h1>ROCK PAPER SCISSORS</h1>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">Smart AI Opponent • Stat Tracker</p>

        <!-- Game Controls -->
        <div class="settings-bar">
            <div>
                <label for="matchLimit">Mode: </label>
                <select id="matchLimit" onchange="resetGame()">
                    <option value="0">Endless Freeplay</option>
                    <option value="3">First to 3 Wins</option>
                    <option value="5">First to 5 Wins</option>
                </select>
            </div>
            <button class="btn-action" onclick="resetGame()">Reset Stats</button>
        </div>

        <!-- Dashboard -->
        <div class="scoreboard">
            <div class="stat-box">
                <div class="stat-val" id="playerScore" style="color: var(--win);">0</div>
                <div class="stat-label" id="scoreLabel">Player</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" id="cpuScore" style="color: var(--lose);">0</div>
                <div class="stat-label">CPU AI</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" id="streakVal" style="color: var(--tie);">0</div>
                <div class="stat-label">Streak</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" id="winRateVal">0%</div>
                <div class="stat-label">Win Rate</div>
            </div>
        </div>

        <!-- Battle Arena -->
        <div class="arena">
            <div class="fighter">
                <div class="choice-icon" id="pChoice">❓</div>
                <div class="fighter-name" id="arenaPlayerName">Player</div>
            </div>
            <div class="vs-badge">VS</div>
            <div class="fighter">
                <div class="choice-icon" id="cChoice">❓</div>
                <div class="fighter-name">Smart AI</div>
            </div>
        </div>

        <!-- Result Box -->
        <div class="result-box">
            <div class="result-title" id="resultTitle">Make Your Move</div>
            <div class="result-sub" id="resultSub">Choose Rock, Paper, or Scissors below.</div>
        </div>

        <!-- Weapon Choice Buttons -->
        <div class="weapon-buttons">
            <button class="btn-weapon" onclick="playRound('rock')" title="Rock">🪨</button>
            <button class="btn-weapon" onclick="playRound('paper')" title="Paper">📄</button>
            <button class="btn-weapon" onclick="playRound('scissors')" title="Scissors">✂️</button>
        </div>
    </div>

    <script>
        const EMOJIS = { rock: '🪨', paper: '📄', scissors: '✂️' };

        // Sound Synthesizer using Web Audio API
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playTone(freq, type, duration) {
            try {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = type;
                osc.frequency.value = freq;
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                gain.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + duration);
                osc.stop(audioCtx.currentTime + duration);
            } catch(e) {}
        }

        function playSound(type) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
            if (type === 'click') playTone(400, 'sine', 0.1);
            if (type === 'win') { playTone(523.25, 'triangle', 0.15); setTimeout(() => playTone(659.25, 'triangle', 0.25), 100); }
            if (type === 'lose') { playTone(300, 'sawtooth', 0.2); setTimeout(() => playTone(200, 'sawtooth', 0.3), 150); }
            if (type === 'tie') playTone(350, 'square', 0.15);
        }

        // Initialize User
        let username = localStorage.getItem('rps_username');
        if (!username) {
            document.getElementById('userModal').style.display = 'flex';
        } else {
            updateUsernameUI(username);
        }

        function saveUsername() {
            const input = document.getElementById('usernameInput').value.trim();
            username = input || 'Player';
            localStorage.setItem('rps_username', username);
            updateUsernameUI(username);
            document.getElementById('userModal').style.display = 'none';
        }

        function openUserModal() {
            document.getElementById('usernameInput').value = username || '';
            document.getElementById('userModal').style.display = 'flex';
        }

        function updateUsernameUI(name) {
            document.getElementById('displayUsername').textContent = name;
            document.getElementById('scoreLabel').textContent = name;
            document.getElementById('arenaPlayerName').textContent = name;
        }

        async function playRound(userChoice) {
            playSound('click');
            const matchLimit = document.getElementById('matchLimit').value;

            const response = await fetch('/play', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ choice: userChoice, match_limit: parseInt(matchLimit) })
            });

            const data = await response.json();

            // Animate choices
            const pElem = document.getElementById('pChoice');
            const cElem = document.getElementById('cChoice');

            pElem.textContent = EMOJIS[data.user_choice];
            cElem.textContent = EMOJIS[data.computer_choice];

            pElem.classList.remove('bounce');
            cElem.classList.remove('bounce');
            void pElem.offsetWidth; // trigger reflow
            pElem.classList.add('bounce');
            cElem.classList.add('bounce');

            // Update stats
            document.getElementById('playerScore').textContent = data.scores.user;
            document.getElementById('cpuScore').textContent = data.scores.computer;
            document.getElementById('streakVal').textContent = data.scores.streak;
            document.getElementById('winRateVal').textContent = data.scores.win_rate + '%';

            // Outcome Display & Audio
            const titleElem = document.getElementById('resultTitle');
            if (data.outcome === 'win') {
                titleElem.textContent = `${username} Wins Round! 🎉`;
                titleElem.style.color = 'var(--win)';
                playSound('win');
            } else if (data.outcome === 'lose') {
                titleElem.textContent = 'CPU Wins Round! 🤖';
                titleElem.style.color = 'var(--lose)';
                playSound('lose');
            } else {
                titleElem.textContent = "It's a Tie! 🤝";
                titleElem.style.color = 'var(--tie)';
                playSound('tie');
            }

            document.getElementById('resultSub').textContent = data.detail;

            // Check match win
            if (data.match_winner) {
                if (data.match_winner === 'user') {
                    confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
                    titleElem.textContent = `🏆 ${username} WINS THE MATCH!`;
                } else {
                    titleElem.textContent = `💀 CPU WINS THE MATCH!`;
                }
            }
        }

        async function resetGame() {
            playSound('click');
            await fetch('/reset', { method: 'POST' });
            document.getElementById('playerScore').textContent = '0';
            document.getElementById('cpuScore').textContent = '0';
            document.getElementById('streakVal').textContent = '0';
            document.getElementById('winRateVal').textContent = '0%';
            document.getElementById('pChoice').textContent = '❓';
            document.getElementById('cChoice').textContent = '❓';
            document.getElementById('resultTitle').textContent = 'Game Reset';
            document.getElementById('resultTitle').style.color = 'var(--text-main)';
            document.getElementById('resultSub').textContent = 'Ready for a new match!';
        }
    </script>
</body>
</html>
"""

def init_session():
    if "user_score" not in session:
        session["user_score"] = 0
        session["computer_score"] = 0
        session["ties"] = 0
        session["streak"] = 0
        session["history"] = []

@app.route("/")
def index():
    init_session()
    return render_template_string(HTML_TEMPLATE)

@app.route("/play", methods=["POST"])
def play():
    init_session()
    data = request.get_json()
    user_choice = data.get("choice")
    match_limit = data.get("match_limit", 0)

    # Adaptive Smart AI Move Prediction
    # AI checks player's most frequent move history to counter it
    history = session.get("history", [])
    if history and len(history) >= 2:
        # Predict user repeats or picks most frequent move
        most_common = max(set(history), key=history.count)
        # Counter move to most common
        counters = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
        # 60% chance to counter player's favorite move, 40% random
        computer_choice = counters[most_common] if random.random() < 0.6 else random.choice(CHOICES)
    else:
        computer_choice = random.choice(CHOICES)

    # Save choice to history
    history.append(user_choice)
    session["history"] = history[-10:] # Keep last 10 moves

    # Round Outcome Logic
    match_winner = None
    if user_choice == computer_choice:
        outcome = "tie"
        detail = f"Both picked {user_choice.capitalize()}."
        session["ties"] += 1
        session["streak"] = 0
    elif BEATS[user_choice] == computer_choice:
        outcome = "win"
        verb = ACTION_VERBS.get((user_choice, computer_choice), "beats")
        detail = f"{user_choice.capitalize()} {verb} {computer_choice.capitalize()}!"
        session["user_score"] += 1
        session["streak"] += 1
    else:
        outcome = "lose"
        verb = ACTION_VERBS.get((computer_choice, user_choice), "beats")
        detail = f"{computer_choice.capitalize()} {verb} {user_choice.capitalize()}!"
        session["computer_score"] += 1
        session["streak"] = 0

    # Calculate Win Rate Percentage
    total_rounds = session["user_score"] + session["computer_score"] + session["ties"]
    win_rate = round((session["user_score"] / total_rounds) * 100) if total_rounds > 0 else 0

    # Match Target Limit Check
    if match_limit > 0:
        if session["user_score"] >= match_limit:
            match_winner = "user"
        elif session["computer_score"] >= match_limit:
            match_winner = "computer"

    return jsonify({
        "user_choice": user_choice,
        "computer_choice": computer_choice,
        "outcome": outcome,
        "detail": detail,
        "scores": {
            "user": session["user_score"],
            "computer": session["computer_score"],
            "streak": session["streak"],
            "win_rate": win_rate
        },
        "match_winner": match_winner
    })

@app.route("/reset", methods=["POST"])
def reset():
    session["user_score"] = 0
    session["computer_score"] = 0
    session["ties"] = 0
    session["streak"] = 0
    session["history"] = []
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(debug=True)