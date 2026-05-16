const { getPokemonName } = require('./utils');

function showBattleActions(request) {
    const side = request.side;

    console.log(`\n=== Actions for ${side.name} ===`);

    const active = request.active?.[0];

    if (request.forceSwitch) {
        console.log('Must switch:');
        side.pokemon.forEach((p, i) => {
            if (!p.fainted) {
                console.log(`  switch ${i + 1} -> ${getPokemonName(p)}`);
            }
        });
        return;
    }

    if (active) {
        console.log('\nMoves:');
        active.moves.forEach((m, i) => {
            console.log(`  move ${i + 1} -> ${m.move} (${m.pp}/${m.maxpp})`);
        });

        console.log('\nSwitches:');
        side.pokemon.forEach((p, i) => {
            if (!p.fainted && !p.active) {
                console.log(`  switch ${i + 1} -> ${getPokemonName(p)}`);
            }
        });
    }
}

module.exports = { showBattleActions };