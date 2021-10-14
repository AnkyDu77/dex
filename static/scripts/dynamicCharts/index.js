const chartContainer = document.getElementById('chartContainer');
let width = chartContainer.width;
let height = chartContainer.height;

const candleSeriesProperties = {
    width: width,
    height: height,
    layout: {
        backgroundColor: 'rgba(255,255,255, 1)',
        textColor: '#546DAD',
        fontFamily: 'Open Sans',
        border: '1px solid red',
    },
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
    },
    grid: {
        vertLines: {
            color: 'rgba(0, 0, 0, 0.05)',
        },
        horzLines: {
            color: 'rgba(0, 0, 0, 0.05)',
        },
    },
    rightPriceScale: {
        visible: true,
        borderColor: 'rgba(0, 0, 0, 0.05)',
        scaleMargins: {
            bottom: 0.2,
        },
    },
    leftPriceScale: {
        visible: true,
        borderColor: 'rgba(0, 0, 0, 0.05)',
        scaleMargins: {
            top: 0.9,
            bottom: 0,
        },
    },
    timeScale: {
        borderVisible: false,
        tickMarkFormatter: (time) => {
            const date = new Date(time*1000);
            return (date.getDate() < 10 ? `0${date.getDate()}`: date.getDate()).toString() + '/' + ((date.getMonth() + 1) < 10 ?  `0${(date.getMonth() + 1)}` : (date.getMonth() + 1)).toString() + ' ' + (date.getHours() < 10 ? `0${date.getHours()}`: date.getHours()).toString() + ':' + (date.getMinutes() < 10 ? `0${date.getMinutes()}`: date.getMinutes()).toString(); //Shows interval beginning
        },
    },
}

const chart = LightweightCharts.createChart(chartContainer,candleSeriesProperties);
const candleSeries = chart.addCandlestickSeries({
    priceScaleId: 'right',
    // upColor: '#A9D8B8',
    // downColor: '#FE938C',
    // borderDownColor: '#FE938C',
    // borderUpColor: '#A9D8B8',
    // wickDownColor: '#FE938C',
    // wickUpColor: '#A9D8B8',

    upColor: '#94BFBE',
    downColor: '#F0899C',
    borderDownColor: '#F0899C',
    borderUpColor: '#94BFBE',
    wickDownColor: '#F0899C',
    wickUpColor: '#94BFBE',

    // upColor: '#8299FE',
    // downColor: 'transparent',
    // borderDownColor: '#8299FE',
    // borderUpColor: '#8299FE',
    // wickDownColor: '#8299FE',
    // wickUpColor: '#8299FE',
});

const volumeSeries = chart.addHistogramSeries({
    color: 'rgba(130,153,254,0.5)',
    priceFormat: {
        type: 'volume',
    },
    priceScaleId: 'left',
});

const toolTipWidth = 60; //100
const toolTipHeight = 80; //80
const toolTipMargin = 15; //15
const maxWidth = 600;
const maxHeight = 300;

const toolTip = document.getElementById('tool-tip');

chart.subscribeCrosshairMove(param => {
    if (!param.time || param.point.x < 0 || param.point.x > width || param.point.y < 0 || param.point.y > height) {
        toolTip.style.display = 'none';
        return;
    }

    toolTip.style.display = 'block';
    let prices = param.seriesPrices.get(candleSeries);
    let volume = param.seriesPrices.get(volumeSeries);
    toolTip.innerHTML = '<div style="color: #546DAD"><div class="tool-tip-content">' + 'O: ' + prices.open +
        '</div><div class="tool-tip-content">' + 'H: ' + prices.high + '</div><div class="tool-tip-content">' +
        'L: ' + prices.low + '</div><div class="tool-tip-content">' + 'C: ' + prices.close + '</div>' +
        '<div class="tool-tip-content">' + 'V: ' + volume + '</div>' +'</div>';

    let left = param.point.x + toolTipMargin;

    if (left > maxWidth - toolTipWidth) {
        left = param.point.x - toolTipMargin - toolTipWidth;
    }

    let top = param.point.y + toolTipMargin;

    if (top > maxHeight - toolTipHeight) {
        top = param.point.y - toolTipHeight - toolTipMargin;
    }

    toolTip.style.left = left + 'px';
    toolTip.style.top = top + 'px';
});
