const readline = require('readline');

const { StreamEngine } = require('./stream_engine');
const { showBattleActions, showSwitches } = require('./action_view');
const { inspectBattleTeamsFromRequest } = require('./team_inspector');
const { printBattleOutput } = require('./output_viewer');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const ask = (q) => new Promise(res => rl.question(q, res));
const engine = new StreamEngine();

const lastError = {
    p1: null,
    p2: null
};

const pendingResolve = {
    p1: null,
    p2: null
};

function parseRequest(line) {
    if (!line.includes('|request|')) return null;
    return JSON.parse(line.split('|request|')[1]);
}
function printRequest(req) {
    console.log(JSON.stringify(req, null, 2));
}

function detectError(line) {
    if (line.startsWith('|error|')) {

        if (lastSide) {
            lastError[lastSide] = line;
        }

        console.log('\n* ERROR:', line.replace('|error|', ''));
        return true;
    }
    return false;
}

function getRequestType(req) {
    if (req.wait) return 'wait';
    if (req.forceSwitch) return 'forceSwitch';
    if (req.active) return 'move';
    return 'unknown';
}

function handleWait(req) {
    console.log(`⏳ ${req.side.name} is waiting...`);
}

function handleMoveRequest(req) {
    console.log(`\n🎯 ${req.side.name} must choose a MOVE or SWITCH`);
    showBattleActions(req);
}

function handleForceSwitch(req) {
    console.log(`\n🔁 ${req.side.name} must SWITCH Pokémon`);
    showSwitches(req);
}

function isValidSwitch(req, index) {
    const p = req.side.pokemon[index - 1];
    if (!p) return false;

    if (p.fainted || p.condition === '0 fnt') return false;
    if (p.active) return false;

    return true;
}

async function handleRequestUI(req, playerId) {
    const type = getRequestType(req);

    if (type === 'wait') {
        handleWait(req);
        return;
    }

    if (type === 'move') handleMoveRequest(req);
    if (type === 'forceSwitch') handleForceSwitch(req);

    while (true) {
        const action = await choose(req);

        if (!action) continue;

        engine.write(`>${playerId} ${action}`);

        // instead of waiting → mark pending
        pendingResolve[playerId] = {
            req,
            action
        };

        return;
    }
}

async function choose(req) {
    const type = getRequestType(req);

    let prompt = `\nAction (${req.side.name})`;

    if (type === 'forceSwitch') prompt += ' [switch only]';
    else if (type === 'move') prompt += ' [move/switch]';

    prompt += ': ';

    const input = await ask(prompt);
    const trimmed = input.trim();

    // ---- MOVE / SWITCH PARSING ----
    if (trimmed.startsWith('switch')) {
        const parts = trimmed.split(' ');
        const index = parseInt(parts[1], 10);

        if (!isValidSwitch(req, index)) {
            console.log('❌ Invalid switch (fainted or active Pokémon)');
            return undefined; // IMPORTANT FIX
        }

        return `switch ${index}`;
    }

    return trimmed;
}

async function run() {
    let pendingRequests = {};
    let bufferOutput = [];
    let pregameBuffer = [];
    let inBattle = false;

    for await (const line of engine.read()) {
        //console.log("LINE CHECK:")
        //console.log(line)
        if (line === 'p1' || line === 'p2') {
            lastSide = line;
            continue;
        }

        if (detectError(line)) continue;
        if (line.startsWith('|turn|')) {
            printBattleOutput(bufferOutput);
            bufferOutput = [];
            console.log(`\n================ TURN ${line.split('|')[2]} ================\n`);
            continue;
        }

        if (line.startsWith('|error|')) {
            console.log('\n* ERROR:', line.replace('|error|', ''));
            const side = lastSide;
            if (pendingResolve[side]) {
                console.log(`\n${side} must retry action`);
                // clear pending so they can re-enter loop
                pendingResolve[side] = null;
            }
            continue;
        }

        if (line.includes('|request|')) {
            const request = parseRequest(line);
            if (!request) continue;
            //printRequest(request);

            const side = request.side;
            console.log('\n=================================================');
            //inspectBattleTeamsFromRequest(request)
            console.log('=================================================\n');
            await handleRequestUI(request, side.id);
            continue;
        }

        // =========================
        // 3. OUTPUT LOGS
        // =========================
        if (!inBattle) {
            pregameBuffer.push(line);
        } else {
            bufferOutput.push(line);
        }
    }
}

run();