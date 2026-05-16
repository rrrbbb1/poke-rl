function formatBattleLine(line) {
    console.log(line)
    if (!line || !line.includes('|')) return null;
    
    const parts = line.split('|');
    const tag = parts[1];

    switch (tag) {
        case 'turn':
            return `\n================ TURN ${parts[2]} ================\n`;

        case 'move':
            return `${parts[2]} used ${parts[3]}`;

        case '-damage':
            return `${parts[2]} took damage`;

        case '-heal':
            return `${parts[2]} healed`;

        case 'switch':
            return `${parts[2]} switched in`;

        case 'faint':
            return `${parts[2]} fainted`;

        case 'win':
            return `Winner: ${parts[2]}`;

        default:
            return null;
    }
}

function printBattleOutput(lines) {
    for (const line of lines) {
        const formatted = formatBattleLine(line);
        if (formatted) console.log(formatted);
    }
}

module.exports = { printBattleOutput };