const { getPokemonName } = require('./utils');

function showBattleActions(request) {
    const side = request.side;

    console.log(`\n=== Actions for ${side.name} ===`);

    const active = request.active?.[0];

    // --------------------
    // FORCE SWITCH
    // --------------------
    if (request.forceSwitch) {
        console.log('Must switch:');

        side.pokemon.forEach((p, i) => {
            const index = i + 1;

            const isFainted = p.fainted || p.condition.startsWith('0 fnt');
            const isActive = p.active;

            const status = (!isFainted && !isActive) ? '[OK]' : '[DISABLED]';

            console.log(`  switch ${index} -> ${getPokemonName(p)} ${status}`);
        });

        return;
    }

    // --------------------
    // NORMAL TURN
    // --------------------
    if (active) {
        console.log('\nMoves:');
        active.moves.forEach((m, i) => {
            const status = m.disabled ? '[DISABLED]' : '[OK]';
            console.log(`  move ${i + 1} -> ${m.move} (${m.pp}/${m.maxpp}) ${status}`);
        });

        console.log('\nSwitches:');
        side.pokemon.forEach((p, i) => {
            const index = i + 1;

            const isFainted = p.fainted || p.condition.startsWith('0 fnt');
            const isActive = p.active;

            const status = (!isFainted && !isActive) ? '[OK]' : '[DISABLED]';

            console.log(`  switch ${index} -> ${getPokemonName(p)} ${status}`);
        });
    }
}

function showSwitches(req) {
    console.log("Must switch:");

    req.side.pokemon.forEach((p, i) => {
        let status = '';

        if (p.fainted || p.condition === '0 fnt') {
            status = '[FAINTED]';
        }
        else if (p.active) {
            status = '[ACTIVE]';
        }
        else {
            status = '[OK]';
        }

        console.log(`  switch ${i + 1} -> ${p.details} ${status}`);
    });
}

module.exports = { showBattleActions, showSwitches };