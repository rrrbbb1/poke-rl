const { BattleStream } = require('../../pokemon_showdown/dist/sim/battle-stream');

class StreamEngine {
    constructor(formatid = 'gen9randombattle') {
        this.stream = new BattleStream();
        this.buffer = '';

        this.stream.write(`>start {"formatid":"${formatid}"}`);
        this.stream.write('>player p1 {"name":"Alice"}');
        this.stream.write('>player p2 {"name":"Bob"}');

        this.outputQueue = [];
    }

    write(input) {
        this.stream.write(input);
    }

    async *read() {
        for await (const chunk of this.stream) {
            const lines = chunk.split('\n').filter(Boolean);
            for (const line of lines) {
                yield line;
            }
        }
    }
}

module.exports = { StreamEngine };