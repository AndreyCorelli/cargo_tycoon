class PlainTextParser {
    constructor() {
        this.i = 0;
        this.buffer = '';
    }

    parseResponse(txt) {
        if (!txt) return null;
        let data = {
            start_time_stamp: this.getNextToken(txt).value,
            end_time_stamp: this.getNextToken(txt).value,
            start_time_min: this.getNextToken(txt).value,
            end_time_min: this.getNextToken(txt).value,
            tracks: []
        };

        let track = null;
        while (true) {
            let token = this.getNextToken(txt);
            if (!token) break;

            if (!track) {
                track = {id: token.value, points: []};
                continue;
            }

            if (token.delimiter == '#') {
                data.tracks.push(track);
                track = null;
                continue;
            }

            if (!track.points.length) {
                track.points.push([token.value]);
                continue;
            }

            let lastPoint = track.points[track.points.length - 1];
            if (lastPoint.length == 3) {
                track.points.push([token.value]);
                continue;
            }
            lastPoint.push(token.value);
        }
        this.accumulateTrackTimes(data.tracks);
        return data;
    }

    getNextToken(txt) {
        while (true) {
            if (this.i == txt.length)
                return null;
            let token = {
                value: null,
                delimiter: ''
            };
            if (txt[this.i] == ',') {
                token.value = parseInt(this.buffer);
                this.buffer = '';
                this.i += 1;
                return token;
            }
            if (txt[this.i] == '#') {
                token.delimiter = '#';
                this.buffer = '';
                this.i += 1;
                return token;
            }
            this.buffer += txt[this.i];
            this.i += 1;
        }
    }

    accumulateTrackTimes(tracks) {
        for (let i = 0; i < tracks.length; i++) {
            let track = tracks[i];

            let currentTime = track.points[0][0];
            for (let j = 1; j < track.points.length; j++) {
                currentTime += track.points[j][0];
                track.points[j][0] = currentTime;
            }
        }
    }
}