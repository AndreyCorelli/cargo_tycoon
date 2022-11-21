class PeriodSelector {
    constructor() {
        this.periodsCount = 25;

        this.container = document.querySelector('#period-selector');
        this.dateFmtMonth = { month: 'short' };
        this.dateFmtDay = { day: 'numeric' };
        this.onPeriodSelected = null;

        this.setupDateSelectors();
        this.readServerCachedPeriods();
    }

    readServerCachedPeriods() {
        let uri = 'cached_periods';
        let that = this;

        fetch(uri, {method: "GET"})
        .then(function (response) {
            return response.json();
        })
        .then(function (json) {
            that.updatePeriodStatuses(json);
        })
        .catch(function (error) {
            console.log(error);
        });

    }

    updatePeriodStatuses(data) {
        for (let i = 0; i < data.length; i++) {
            let period = data[i];
            let cell = document.querySelector(
                `[data-start="20${period[0]}"]`);
            if (!cell) continue;
            cell.classList.add('period-cached');
        }
    }

    setupDateSelectors() {
        let intervals = this.get2weekPeriods();
        let markup = '';

        for (let i = 0; i < intervals.length; i++) {
            let interval = intervals[i];
            let startDate = interval[0], endDate = interval[1];

            let yearPart = '', prevYearPart = '';
            if (startDate.getYear() != endDate.getYear()) {
                prevYearPart = ` ${startDate.getFullYear()}`;
                yearPart = ` ${endDate.getFullYear()}`;
            }

            let startDateStr = `${startDate.getFullYear()}-${startDate.getMonth() + 1}-${startDate.getDate()}`;
            let endDateStr = `${endDate.getFullYear()}-${endDate.getMonth() + 1}-${endDate.getDate()}`;

            markup += `<div data-start="${startDateStr}" data-end="${endDateStr}">`;
            markup += `${this.formatDateShort(startDate)}${prevYearPart}<hr/>`;
            markup += `${this.formatDateShort(endDate)}${yearPart}</div>`;
        }
        this.container.innerHTML = markup;
        this.setupClickHandler();
    }

    setupClickHandler() {
        const cells = document.querySelectorAll('[data-start]');
        for (let i = 0; i < cells.length; i++) {
            let cell = cells[i];
            const start = cell.getAttribute('data-start'),
                  end = cell.getAttribute('data-end');

            let confirmText = `Load data from ${start} to ${end}?`;
            cell.onclick = () => {
                if (!confirm(confirmText))
                    return;
                this.onPeriodSelected(start, end);
            }
        }
    }

    formatDateShort(d) {
        let month = d.toLocaleDateString("en-US", this.dateFmtMonth);
        let day = d.toLocaleDateString("en-US", this.dateFmtDay);
        return `${day} ${month}`;
    }

    get2weekPeriods() {
      let d = new Date();
      let currentWeek = this.getWeekNumber(d);
      let intervalShift = (currentWeek + 1) % 2;

      // align the interval - let it be multiple by 2 weeks
      d.setDate(d.getDate() - 7 * intervalShift + 7 * 2);
      let endDate = this.getFirstDayOfWeek(d);

      let intervals = [];

      for (let i = 0; i < this.periodsCount; i++) {
          let startDate = new Date(endDate.getTime());
          startDate.setDate(startDate.getDate() - 7 * 2);
          intervals.push([startDate, endDate]);
          endDate = startDate;
      }
      return intervals;
    }

    getWeekNumber(d) {
        d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
        d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay()||7));
        let yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
        let weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1) / 7);
        return weekNo;
    }

    getFirstDayOfWeek(d) {
        d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
        let day = d.getDay();
        let diff = d.getDate() - day + (day === 0 ? -6 : 1);
        return new Date(d.setDate(diff));
    }
}