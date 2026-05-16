function getPokemonName(p) {
    if (!p) return 'Unknown';
    return (
        p.name ||
        p.species ||
        (typeof p.ident === 'string' ? p.ident.split(': ').pop() : null) ||
        'Unknown'
    );
}

function parsePokemon(p) {
    if (!p) return null;

    // --- NAME ---
    const name =
        p.name ||
        (p.ident ? p.ident.split(': ').pop() : null) ||
        'Unknown';

    // --- HP ---
    let hp = null;
    let maxhp = null;

    if (typeof p.condition === 'string' && p.condition.includes('/')) {
        const [a, b] = p.condition.split('/');
        hp = Number(a);
        maxhp = Number(b);
    }

    // --- TYPE SAFETY ---
    const stats = p.stats || {};
    const moves = p.moves || [];

    return {
        // identity
        name,
        ident: p.ident,

        // combat state
        hp,
        maxhp,
        condition: p.condition,

        status: p.status || 'healthy',
        active: !!p.active,

        // gameplay info
        moves,
        item: p.item || null,
        ability: p.ability || p.baseAbility || null,
        teraType: p.teraType || null,
        terastallized: !!p.terastallized,

        // stats
        stats: {
            hp: stats.hp ?? null,
            atk: stats.atk ?? null,
            def: stats.def ?? null,
            spa: stats.spa ?? null,
            spd: stats.spd ?? null,
            spe: stats.spe ?? null
        },

        // raw access if needed (debug / RL extensions)
        _raw: p
    };
}

function printPokemonData(p, raw = false) {
    // If raw mode: just dump the original object
    if (raw) {
        console.log(p);
        return;
    }

    // Otherwise use normalized version
    const mon = parsePokemon(p);

    console.log(`    Name: ${mon.name}`);
    console.log(`    HP: ${mon.hp} / ${mon.maxhp}`);
    console.log(`    Status: ${mon.status}`);

    console.log(`    Moves: ${mon.moves.join(', ') || 'none'}`);
    console.log(`    Item: ${mon.item || 'none'}`);
    console.log(`    Ability: ${mon.ability || 'unknown'}`);

    console.log(`    Tera: ${mon.teraType || 'none'} ${mon.terastallized ? '(active)' : ''}`);

    console.log(`    Stats:`);
    for (const [k, v] of Object.entries(mon.stats)) {
        console.log(`      ${k}: ${v}`);
    }
}

module.exports = { getPokemonName, printPokemonData };