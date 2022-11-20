class MapManager {
    constructor() {
        this.animation = false;
        this.animationPrepared = false;
        this.tracks = [];

        this.canvas = document.querySelector('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        this.ctx.globalAlpha = 0.6;
        this.timing = {
            startMinute: 0,
            endMinute: 1,
            startTime: new Date(),
            endTime: new Date(),
            startTimestamp: 0,
            endTimestamp: 1,
            currentMinute: 0
        };

        this.timeStepMinutes = 30;
        this.sleepInterval = 100;

        // drawing settings
        this.drawingSettings = {
            trackBodyLenMinutes: 1*60,
            trackTailLenMinutes: 4*60,
            colors: [
            '#e02020',
            '#906020',
            '#409020',
            '#20e020',
            '#209040',
            '#206060',
            '#204090',
            '#2060e0']
        };

        this.timerControl = document.querySelector('#play-track');
        this.bannerControl = document.querySelector('#loading-banner');
        this.labelTimeStart = document.querySelector('#label-time-start');
        this.labelTimeEnd = document.querySelector('#label-time-end');
        this.labelTimeCurrent = document.querySelector('#label-time-current');
        this.btnStartStop = document.querySelector('#btn-start-stop');
        this.btnStartStop.onclick = () => { this.onStartStopClick(); }

        this.dateFmtLong = { weekday: 'short', month: 'short', day: 'numeric' };
        this.dateFmtShort = { month: 'short', day: 'numeric' };
        this.timeFmt = { hour12: false, hour: '2-digit', minute: '2-digit' };
    }

    queryTracks(prefix) {
        // ${encodeURIComponent(prefix)}
        let uri = `track_data?year=2022&week=30`;
        let that = this;

        this.stopAnimation();
        this.animationPrepared = false;
        this.showHideLoadingBanner(true);
        this.btnStartStop.enabled = false;
        this.btnStartStop.value = "start";

        fetch(uri, {method: "GET"})
        .then(function (response) {
            that.showHideLoadingBanner(false);
            return response.json();
        })
        .then(function (json) {
            that.prepareAnimation(json);
        })
        .catch(function (error) {
            console.log(error);
        });
    }

    prepareAnimation(json) {
        this.tracks = json.data;
        this.timing = {
            startMinute: json.start_time_min,
            endMinute: json.end_time_min,
            startTime: new Date(json.start_time_stamp * 1000),
            endTime: new Date(json.end_time_stamp * 1000),
            startTimestamp: json.start_time_stamp,
            endTimestamp: json.end_time_stamp,
            currentMinute: json.start_time_min
        };
        this.setScale();
        this.animationPrepared = true;
        this.btnStartStop.enabled = true;
        console.log(`${this.tracks.length} trucks received`);

        this.startAnimation();
    }

    onStartStopClick() {
        if (this.animation) {
            this.stopAnimation();
            return;
        }
        if (!this.animationPrepared)
            return;
        this.startAnimation();
    }

    startAnimation() {
        this.animation = true;
        this.btnStartStop.value = "pause";
        this.goToFrame(this.timing.currentMinute);

        setTimeout(() => {
            this.timeForward();
        }, this.sleepInterval);
    }

    stopAnimation() {
        this.animation = false;
        this.btnStartStop.value = "start";
    }

    timeForward() {
        if (this.timing.currentMinute == this.timing.endMinute) {
            this.stopAnimation();
            return false;
        }
        let minute = this.timing.currentMinute + this.timeStepMinutes;
        minute = Math.min(minute, this.timing.endMinute);
        this.goToFrame(minute);
        if (this.animation)
            if (minute < this.timing.endMinute)
                setTimeout(() => {
                    this.timeForward();
                }, this.sleepInterval);
    }

    setScale() {
        console.log(this.timing);
        this.timerControl.min = this.timing.startMinute;
        this.timerControl.max = this.timing.endMinute;
        this.timerControl.position = this.timing.currentMinute;

        this.labelTimeStart.innerHTML = this.getTimeString(
            this.getTimeFromMinute(this.timerControl.min));
        this.labelTimeEnd.innerHTML = this.getTimeString(
            this.getTimeFromMinute(this.timerControl.max));
    }

    goToFrame(frameTime, updateTrackPosition) {
        if (updateTrackPosition === undefined)
            updateTrackPosition = true;
        if (updateTrackPosition)
            this.timerControl.value = frameTime;

        this.timing.currentMinute = frameTime;
        this.drawFrame();
        this.labelTimeCurrent.innerHTML = this.getTimeString(this.getTimeFromMinute(frameTime), 'l');
    }

    getTimeFromMinute(minute) {
        if (this.timing.endMinute == this.timing.startMinute)
            return '-';
        minute -= this.timing.startMinute;
        let relTime = minute / (this.timing.endMinute - this.timing.startMinute);
        let second = (this.timing.endTimestamp - this.timing.startTimestamp) * relTime;
        second += this.timing.startTimestamp;
        return new Date(Math.round(1000 * second));
    }

    getTimeString(tm, fmt) {
        let datePart = '';
        if (fmt == 'l')
            datePart = tm.toLocaleDateString("en-US", this.dateFmtLong);
        else
            datePart = tm.toLocaleDateString("en-US", this.dateFmtShort);
        let timePart = tm.toLocaleTimeString("en-US", this.timeFmt);
        return `${datePart}<br/>${timePart}`;
    }

    drawFrame() {
        let frameTime = this.timing.currentMinute;
        //let startDate = new Date();
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        let tailTime = frameTime - this.drawingSettings.trackTailLenMinutes;
        let bodyTime = frameTime - this.drawingSettings.trackBodyLenMinutes;

        for (let i = 0; i < this.tracks.length; i++) {
            let track = this.tracks[i];
            this.drawTrack(track, frameTime, tailTime, bodyTime);
        }
        //let endDate   = new Date();
        //let mils = (endDate.getTime() - startDate.getTime());
        //console.log('Mils elapsed: ' + mils);
    }

    drawTrack(track, frameTime, tailTime, bodyTime) {
        let firstPointTime = track[1][0][0];
        if (firstPointTime > frameTime)
            return;
        let lastPointTime = track[1][track[1].length - 1][0];
        if (lastPointTime < tailTime)
            return;

        let tailPoints = [], bodyPoints = [];
        for (let i = 0; i < track[1].length; i++) {
            let point = track[1][i];
            let tm = point[0];
            // TODO: use simple optimization to find a start and the end indices
            if (tm < tailTime) continue;
            if (tm > frameTime) break;
            if (tm < bodyTime) {
                tailPoints.push([point[1], point[2]]);
                continue;
            }
            bodyPoints.push([point[1], point[2]]);
        }
        if (!tailPoints.length && !bodyPoints.length) return;
        let color = this.pickColorByTrackIndex(track[0]);
        this.drawTrackOnCanvas(color, tailPoints, bodyPoints);
    }

    pickColorByTrackIndex(i) {
        let index = i % this.drawingSettings.colors.length;
        return this.drawingSettings.colors[index];
    }

    drawTrackOnCanvas(color, tailPoints, bodyPoints) {
        let thicks = [1, 3];
        let polys = [tailPoints, bodyPoints];

        for (let i = 0; i < 2; i++) {
            let points = polys[i];
            if (points.length < 2) continue;

            this.ctx.beginPath();
            this.ctx.lineWidth = thicks[i];
            this.ctx.strokeStyle = color;
            this.ctx.moveTo(points[0][0], points[0][1]);
            for (let j = 1; j < points.length; j++) {
                this.ctx.lineTo(points[j][0], points[j][1]);
            }
            this.ctx.stroke();
        }
    }

    showHideLoadingBanner(show) {
        this.bannerControl.style.display = show ? 'block' : 'none';
    }
}