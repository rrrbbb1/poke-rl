const { printPokemonData } = require('./utils');


function inspectBattleTeamsFromRequest(request) {
    const side = request.side;

    console.log(`\n=== ${side.name} ===`);

    const active = side.active?.[0];
    if (active) {
        console.log(`Active: ${active.name || active.species}`);
        console.log(`HP: ${active.hp}/${active.maxhp}`);
    }

    console.log('\nTeam:');

    side.pokemon.forEach((p, i) => {
        console.log(`\n  ${i + 1}.`);
        printPokemonData(p);
    });
}

module.exports = { inspectBattleTeamsFromRequest };