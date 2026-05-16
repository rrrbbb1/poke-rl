const readline = require('readline');
const { StreamEngine } = require('./stream_engine');
const { inspectBattleTeamsFromRequest } = require('./team_inspector');
const { showBattleActions } = require('./action_view');
const { printBattleOutput } = require('./output_viewer');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const ask = (q) => new Promise(res => rl.question(q, res));

const engine = new StreamEngine();

function parseRequest(line) {
    if (!line.includes('|request|')) return null;
    return JSON.parse(line.split('|request|')[1]);
}

// --------------------
// choose action
// --------------------
async function choose(req) {
    showBattleActions(req);

    const input = await ask(`\nAction (${req.side.name}): `);
    return input.trim();
}

// --------------------
// main loop
// --------------------
async function run() {
    let pendingRequests = {};
    let bufferOutput = [];
    let pregameBuffer = [];
    let inBattle = false;

    for await (const line of engine.read()) {

        // =========================
        // 0. DETECT TURN BOUNDARY
        // =========================
        if (line.startsWith('|turn|')) {
            // turn fully resolved → safe to flush
            printBattleOutput(bufferOutput);
            bufferOutput = [];

            console.log(`\n================ TURN ${line.split('|')[2]} ================\n`);

            continue;
        }

        // =========================
        // 1. REQUEST HANDLING
        // =========================
        if (line.includes('|request|')) {

            const request = parseRequest(line);
            if (!request) continue;

            const side = request.side;

            // ---- FIRST TIME WE ENTER BATTLE ----
            if (!inBattle) {
                console.log('\n========= BATTLE START =========\n');
                printBattleOutput(pregameBuffer);
                pregameBuffer = [];
                inBattle = true;
            }

            console.log('\n=================================================');
            //inspectBattleTeamsFromRequest(request)
            console.log('=================================================\n');

            pendingRequests[side.id] = request;

            // ---- BOTH PLAYERS READY ----
            if (pendingRequests.p1 && pendingRequests.p2) {

                const a1 = await choose(pendingRequests.p1);
                const a2 = await choose(pendingRequests.p2);

                engine.write(`>p1 ${a1}`);
                engine.write(`>p2 ${a2}`);

                pendingRequests = {};
            }

            continue;
        }

        // =========================
        // 2. OUTPUT LOGS
        // =========================
        if (!inBattle) {
            pregameBuffer.push(line);
        } else {
            bufferOutput.push(line);
        }
    }
}

run();