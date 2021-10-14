$(function () {
    const $switchButton = document.getElementById('switch');
    const $btnText = document.getElementById('btn-text');
    const $btn = document.getElementById('btn');
    const $priceInput = document.getElementById('price-input');
    const $amountInput = document.getElementById('amount-input');
    const $totalPrice = document.getElementById('total-price');
    const $searchElement = document.getElementById('search-input');
    const $listElement = document.getElementById('list');
    const $currentPairLabel = document.getElementById('current-cryptocurrency-pair');
    const $firstCryptocurrencyLabel = document.getElementById('first-cryptocurrency');
    const $secondCryptocurrencyLabel = document.getElementById('second-cryptocurrency');
    const $totalCryptocurrencyLabel = document.getElementById('total-cryptocurrency');
    const $tablePriceCol1 = document.getElementById('table-price-col-1');
    const $tablePriceCol2 = document.getElementById('table-price-col-2');
    const $tableAmountCol1 = document.getElementById('table-amount-col-1');
    const $tableAmountCol2 = document.getElementById('table-amount-col-2');
    const $asksTable = document.getElementById('asks-table');
    const $bidsTable = document.getElementById('bids-table');
    const $loader = document.getElementById('loader');
    const $loader2 = document.getElementById('loader-2');
    const $authError = document.getElementById('auth-error');
    const $loginBtn = document.getElementById('login-btn');
    const $signUpBtn = document.getElementById('signup-btn');
    const $totalAndBtnWrapper = document.getElementById('total-and-btn-wrapper');
    const $totalPriceField = document.getElementById('total-price-field');
    const $authButtons = document.getElementById('auth-buttons');
    const $accButtons = document.getElementById('acc-buttons');
    const $accButton = document.getElementById('acc-btn');
    const $exitBtn = document.getElementById('exit-btn');
    const $accAddress = document.getElementById('account-address');
    const $tokensListElement = document.getElementById('tokens-list');
    const $copyIcon = document.getElementById('copy-icon');
    const $copyMessage = document.getElementById('copy-message-with-triangle');
    const $accountWrapper = document.getElementById('account-wrapper');
    const $sendBtn = document.getElementById('send-btn');
    const $authErrorSecondTab = document.getElementById('auth-error-second-tab');
    const $sendBtnText = document.getElementById('send-btn-text');
    const $recipientInput = document.getElementById('recipient-input');
    const $zshAmountInput = document.getElementById('zsh-amount-input');
    const $openOrdersContent = document.getElementById('open-orders-content');
    const $ordersHistoryContent = document.getElementById('orders-history-content');
    const $intervalButtons = document.getElementById('interval-buttons');

    //const API_URL = 'http://192.168.0.100:5000';
    const API_URL = 'http://localhost:5000'; // Alina
    //const API_URL = 'http://4a9b-77-222-104-154.ngrok.io';
    const TRADE_DIRECTIONS = {SELL: 'SELL', BUY: 'BUY'};
    let tradeDirection = TRADE_DIRECTIONS.BUY;

    let greenColor = "#94BFBE"; //B1CC74 B9FFB7
    let redColor = "#F0899C";
    const $primaryColor = "#546DAD"
    const $error = redColor;
    const $success = greenColor; //"#9FAF90";

    const cryptocurrencyPairs = ['ZSH/USDT', 'BTC/USDT', 'BTC/DAI', 'ETH/USDT', 'ETH/DAI', 'BNB/USDT', 'BNB/DAI', 'DOT/USDT',
        'DOT/DAI', 'UNI/USDT', 'UNI/DAI', 'BTC/ETH', 'ETH/UNI', 'BTC/DOT', 'ETH/DOT']

    const defaultCryptocurrencyPair = 'ZSH/USDT';
    let currentCryptocurrencyPair = defaultCryptocurrencyPair;
    let firstCryptocurrency = defaultCryptocurrencyPair.substring(0, defaultCryptocurrencyPair.indexOf('/'));
    let secondCryptocurrency = defaultCryptocurrencyPair.substring(defaultCryptocurrencyPair.indexOf('/') + 1,
        defaultCryptocurrencyPair.length);
    let balances = [];
    let language = localStorage.getItem('language');

    const setPhraseLanguage = (element, russianPhrase, englishPhrase) => {
        language = localStorage.getItem('language');
        if (language === "rus" || language === null)
            element.innerText = russianPhrase;
        else
            element.innerText = englishPhrase;
    }

    const setCryptocurrency = (currentPair) => {
        $currentPairLabel.innerText = currentPair;
        currentCryptocurrencyPair = currentPair;
        firstCryptocurrency = currentCryptocurrencyPair.substring(0, currentCryptocurrencyPair.indexOf('/'));
        secondCryptocurrency = currentCryptocurrencyPair.substring(currentCryptocurrencyPair.indexOf('/') + 1,
            currentCryptocurrencyPair.length);


        if ($('#switch').prop('checked')) {
            setPhraseLanguage($btnText, `Продать ${firstCryptocurrency}`, `Sell ${firstCryptocurrency}`);
        }
        else {
            setPhraseLanguage($btnText, `Купить ${firstCryptocurrency}`, `Buy ${firstCryptocurrency}`);
        }
        $secondCryptocurrencyLabel.innerText = secondCryptocurrency;
        $firstCryptocurrencyLabel.innerText = firstCryptocurrency;
        $totalCryptocurrencyLabel.innerText = secondCryptocurrency;

        setPhraseLanguage($tablePriceCol1, `Цена(${secondCryptocurrency})`, `Price(${secondCryptocurrency})`)
        setPhraseLanguage($tableAmountCol1, `Количество(${firstCryptocurrency})`, `Amount (${firstCryptocurrency})`)
        setPhraseLanguage($tablePriceCol2, `Цена(${secondCryptocurrency})`, `Price(${secondCryptocurrency})`)
        setPhraseLanguage($tableAmountCol2, `Количество(${firstCryptocurrency})`, `Amount (${firstCryptocurrency})`)

        // setChartData();
    }

    const setBalance = async () => {
        balances = [];
        $tokensListElement.innerText = '';
        try {
            let address = localStorage.getItem('walletAddress');
            let result = await postData(`${API_URL}/wallet/getBalance`, {address});
            balances =  (await result.json())['BALACNES'];
            balances.forEach(item => {
                listItem = document.createElement('li');
                listItem.innerHTML = `${Math.round(parseFloat(item.balance) * 10**(decimals)) / 10**(decimals)} ${item.token}`;
                $tokensListElement.appendChild(listItem);
            })
        } catch (e) {
            console.log(e)
        }
    }

    window.addEventListener("load", async function (event) {
        makeList();
        createTable($asksTable);
        createTable($bidsTable);
        setCryptocurrency(defaultCryptocurrencyPair);
        setChartData();
        let walletAddress = localStorage.getItem('walletAddress');
        if (walletAddress === null) {
            showAuthError();
        } else {
            $accAddress.innerText = getShortAddress(walletAddress);
            await setBalance();
            $authButtons.style.display = "none";
            $accButtons.style.display = "flex";
        }
        document.getElementById("open-orders-btn").click();
        document.getElementById("limit-order-btn").click();
    }, false);

    window.addEventListener("mousedown", async function (event) {
        let $accountWindow = document.getElementById('account-window-with-triangle');
        if (event.target !== $accountWindow && !$accountWindow.contains(event.target) && $accountWrapper.style.opacity === "1") {
            $accountWrapper.style.opacity = "0";
            $accButton.style.borderBottomColor = 'transparent';
        }
    })

    $switchButton.onclick = () => {
        if ($('#switch').prop('checked')) {
            setPhraseLanguage($btnText, `Продать ${firstCryptocurrency}`, `Sell ${firstCryptocurrency}`);
            tradeDirection = TRADE_DIRECTIONS.SELL;
        } else {
            setPhraseLanguage($btnText, `Купить ${firstCryptocurrency}`, `Buy ${firstCryptocurrency}`)
            tradeDirection = TRADE_DIRECTIONS.BUY;
        }
    }

    const decimals = 6;

    $priceInput.oninput = () => numericInputHandler($priceInput, decimals, $amountInput, $totalPrice );

    $amountInput.oninput = () => numericInputHandler($amountInput, decimals, $priceInput, $totalPrice );

    const numericInputHandler = (firstInputObject, decimals = 6, secondInputObject = null, totalObject = null) => {
        let { error, value } = processNumericValue(firstInputObject.value, decimals);
        firstInputObject.value = value.toString().replace('.', ',');
        if (secondInputObject !== null && totalObject !== null) {
            if (error === false) {
                let firstValue = value;
                let secondValue = Number(secondInputObject.value.replace(',', '.'));
                if (firstValue >= 0 && secondValue >= 0) totalObject.innerText = (Math.round((firstValue * secondValue) * 10 ** (decimals)) /
                    10 ** (decimals)).toString().replace('.', ',');
            }
        }

    }

    const processNumericValue = (value, decimals) => {
        value = value.replace(/,/g, '.');
        let valueArray = value.split('.');
        if (/[^.,\d]/g.test(value))
            return { error: true, value: value.slice(0, value.length - 1 ) };
        if (valueArray.length > 2)
            return { error: true, value: value.slice(0, value.length - 1 ) };
        if (valueArray[1] && valueArray[1].length > decimals)
            return { error: false, value: value.slice(0, value.length - 1 ) };
        return{ error: false, value };
    }

    $zshAmountInput.oninput = () => {
        const $commissionInfo = document.getElementById('commission-info');
        let commission = Math.round((parseFloat($zshAmountInput.value.replace(',','.')) * 0.0001)*10**6)/10**6;
        setPhraseLanguage($commissionInfo, `Комиссия (0,01%): ${commission} ZSH`, `Commission (0,01%): ${commission} ZSH`)
        numericInputHandler($zshAmountInput, decimals);
    }

    const makeList = () => {
        let numberOfListItems = cryptocurrencyPairs.length,
            listItem,
            i;

        for (i = 0; i < numberOfListItems; ++i) {
            listItem = document.createElement('li');
            listItem.innerHTML = cryptocurrencyPairs[i];
            $listElement.appendChild(listItem);
        }
    }

    $searchElement.onkeyup = () => {
        let i, listItemValue;
        let filter = $searchElement.value.toUpperCase();
        if (filter.indexOf(' ') > -1) filter = filter.replace(' ', '/');
        let li = $listElement.getElementsByTagName('li');

        // Loop through all list items, and hide those who don't match the search query
        for (i = 0; i < li.length; i++) {
            listItemValue = li[i].innerText;
            if (listItemValue.indexOf(filter) > -1) {
                li[i].style.display = "block";
            } else {
                li[i].style.display = "none";
            }
        }
    }

    function getEventTarget(e) {
        e = e || window.event;
        return e.target || e.srcElement;
    }

    // $listElement.onclick = (event) => {
    //     let target = getEventTarget(event).innerText;
    //     if (target.length < 10) setCryptocurrency(target);
    //     clearInterval(refreshOrderBook);
    //     refreshOrderBook = setInterval(orderBook, 5000);
    // }

    let interval = 5; //default 5 minutes

    $intervalButtons.onclick = (event) => {
        let buttons = $intervalButtons.getElementsByTagName('div');
        for (let i = 0; i < buttons.length; i++){
            buttons[i].style.borderColor = 'transparent';
        }
        let target = getEventTarget(event).innerText;
        switch (target) {
            case '5m':
                buttons[0].style.borderColor = 'rgba(255,255,255,0.6)';
                interval = 5;
                setChartData();
                break;
            case '15m':
                buttons[1].style.borderColor = 'rgba(255,255,255,0.6)';
                interval = 15;
                setChartData();
                break;
            case '1h':
                buttons[2].style.borderColor = 'rgba(255,255,255,0.6)';
                interval = 60;
                setChartData()
                break;
            case '4h':
                buttons[3].style.borderColor = 'rgba(255,255,255,0.6)';
                interval = 240;
                setChartData();
                break;
            case '1d':
                buttons[4].style.borderColor = 'rgba(255,255,255,0.6)';
                interval = 1440;
                setChartData();
                break;
        }
    }

    const orderBookLimit = 10;

    const createTable = (container) => {
        let i,
            j,
            tableRow,
            tableCell;

        for (i = 0; i < orderBookLimit; ++i) {
            tableRow = document.createElement('tr');
            container.appendChild(tableRow);
            for (j = 0; j < 3; ++j) {
                tableCell = document.createElement('td');
                tableRow.appendChild(tableCell);
            }
        }
    }

    const getFormattedDate = (date) => {
        return  setZeroAhead(date.getDate()) + '/' + setZeroAhead(date.getMonth() + 1) + '/' + setZeroAhead(date.getFullYear()) + ' '
            + setZeroAhead(date.getHours()) + ':' + setZeroAhead(date.getMinutes())  + ':' + setZeroAhead(date.getSeconds());
    }

    const setZeroAhead = (value) => {
        if (value < 10)
            return `0${value}`;
        else return value;
    };

    const setDataToOpenOrdersTable = (data) => {
        let walletAddress = localStorage.getItem('walletAddress');
        let filteredData = data.tradeOrders.filter(order => {
            return order.sender === walletAddress
        })
        let parsedData = filteredData.map(element => {
            let direction = null;
            let volume = 0;
            let date = new Date(element.timestamp*1000)
            let formattedDate = getFormattedDate(date);
            // first token && second token
            if (element.get === firstCryptocurrency.toLowerCase() && element.send === secondCryptocurrency.toLowerCase()) {
                direction = 'BUY';
                volume = parseFloat(element.getVol).toFixed(decimals);
            }
            // second token && first token
            if (element.get === secondCryptocurrency.toLowerCase() && element.send === firstCryptocurrency.toLowerCase()) {
                direction = 'SELL';
                volume = parseFloat(element.sendVol).toFixed(decimals);
            }
            return [formattedDate, element.symbol.toUpperCase(), 'LIMIT', direction, element.price, volume]
        })

        let infoWrapper = document.getElementById('open-orders-info')
        if (filteredData.length > 0) {
            infoWrapper.style.display = 'none';
            $openOrdersContent.style.display = 'block';
            let openOrdersTable = document.getElementById('open-orders-table-body');
            openOrdersTable.innerHTML = "";
            for (let i = 0; i < filteredData.length; ++i) {
                let tableRow = document.createElement('tr');
                openOrdersTable.appendChild(tableRow);
                for (let j = 0; j < 6; ++j) {
                    let tableCell = document.createElement('td');
                    tableRow.appendChild(tableCell);
                    tableCell.innerText = parsedData[i][j];
                }
            }
        } else {
            $openOrdersContent.style.display = 'none';
            infoWrapper.style.display = 'block';
        }
    }

    const setDataToOrdersHistoryTable = (data) => {
        let walletAddress = localStorage.getItem('walletAddress');
        let filteredData = data.chain.map(block => {
            let filteredTransactions = block.transactions.filter(transaction => {
                return transaction.tradeTxId !== null && transaction.sender === walletAddress;
            })
            return filteredTransactions;
        })

        let mergedData = [].concat.apply([], filteredData.filter(element => element.length !== 0));

        let parsedData = mergedData.map(element => {
            let pair = element.symbol;
            let volume = 0;
            let firstSymbol = pair.substring(0, pair.indexOf('/'));
            let secondSymbol = pair.substring(pair.indexOf('/') + 1, pair.length);
            let direction = null;
            let date = new Date(element.timestamp*1000)
            // let formattedDate = getFormattedDate(date);
            if (element.contract === firstSymbol) {
                direction = 'SELL';
                volume = parseFloat(element.sendAmount).toFixed(decimals);
            }
            if (element.contract === secondSymbol) {
                direction = 'BUY';
                volume = parseFloat(element.recieveAmount).toFixed(decimals);
            }
            let status = 'DONE';
            return [date, element.symbol.toUpperCase(), 'LIMIT', direction, element.price, volume, status]
        })

        parsedData.sort(function(a,b){
            return new Date(b[0]) - new Date(a[0]);
        });
        parsedData.forEach(element => {
            element[0] = getFormattedDate(element[0]);
        })

        let infoWrapper = document.getElementById('orders-history-info')
        if ( mergedData.length > 0) {
            infoWrapper.style.display = 'none';
            $ordersHistoryContent.style.display = 'block';
            let ordersHistoryTable = document.getElementById('orders-history-table-body');
            ordersHistoryTable.innerHTML = "";
            for (let i = 0; i < mergedData.length; ++i) {
                let tableRow = document.createElement('tr');
                ordersHistoryTable.appendChild(tableRow);
                for (let j = 0; j < 7; ++j) {
                    if (j === 5 && parsedData[i][j] === 'DONE')
                    {
                        let tableCell = document.createElement('td');
                        tableRow.appendChild(tableCell);
                        let tableCellText = document.createElement('div');
                        tableCell.appendChild(tableCellText);
                        tableCellText.innerText = parsedData[i][j];
                        tableCellText.style.backgroundColor = greenColor;
                        tableCellText.style.lineHeight = '12px';
                        tableCellText.style.padding = '2px 10px';
                        tableCellText.style.borderRadius = '10px';
                    }
                    else {
                        let tableCell = document.createElement('td');
                        tableRow.appendChild(tableCell);
                        tableCell.innerText = parsedData[i][j];
                    }
                }
            }
        } else {
            $ordersHistoryContent.style.display = 'none';
            infoWrapper.style.display = 'block';
        }
    }

    let orderBookData = {
        asks: [],
        bids: [],
    }

    const descendingOrder = (a, b) => {
        if (a.price > b.price) {
            return -1;
        }
        if (a.price < b.price) {
            return 1;
        }
        return 0;
    }

    const ascendingOrder = (a, b) => {
        if (a.price < b.price) {
            return -1;
        }
        if (a.price > b.price) {
            return 1;
        }
        return 0;
    }

    const parseAndSortData = (data) => {
        orderBookData = {
            asks: [],
            bids: [],
        }

        data.forEach(element => {
            let direction = element.direction;
            if (direction[0] === firstCryptocurrency.toLowerCase() && direction[1] === secondCryptocurrency.toLowerCase()) orderBookData.asks.push({price: element.price, amount: element.amount[0]});
            if (direction[0] === secondCryptocurrency.toLowerCase() && direction[1] === firstCryptocurrency.toLowerCase()) orderBookData.bids.push({price: element.price, amount: element.amount[1]});
        })

        orderBookData.asks.sort(descendingOrder);
        orderBookData.bids.sort(descendingOrder);

    }

    const orderBook = () => {
        fetch(`${API_URL}/getTradeOrders`)
            .then(res => res.json())
            .then(data => {
                setDataToOpenOrdersTable(data);
                const obdata = data.tradeOrders.map(d => {
                    return {price: d.price, direction: [d.send, d.get], amount: [d.sendVol, d.getVol]}
                });
                // limit
                // obdate = obdata.slice(3, obdata.length)
                parseAndSortData(obdata);

                for (let i = 0; i < $asksTable.rows.length - 1; ++i) {
                    let cols = $asksTable.rows[i + 1].getElementsByTagName("td");
                    if (orderBookData.asks[i] !== undefined && i < orderBookData.asks.length) {
                        cols[0].innerText = orderBookData.asks[i].price.toFixed(decimals);
                        cols[0].style.backgroundColor = redColor; // F08CAE EA9EC7
                        cols[0].style.borderRadius = '10px';
                        cols[0].style.textAlign = 'center';
                        cols[0].style.color = '#fff';
                        cols[1].innerText = orderBookData.asks[i].amount.toFixed(decimals);
                        cols[2].innerText = ((cols[0].innerText * cols[1].innerText).toFixed(6)).toString();
                    }
                    else {
                        cols[0].innerText = "";
                        cols[0].style.backgroundColor = 'transparent';
                        cols[1].innerText = "";
                        cols[2].innerText = "";
                    }
                }

                for (let i = 0; i < $bidsTable.rows.length - 1; ++i) {
                    let cols = $bidsTable.rows[i + 1].getElementsByTagName("td");
                    if (orderBookData.bids[i] !== undefined && i < orderBookData.bids.length) {
                        cols[0].innerText = orderBookData.bids[i].price.toFixed(decimals);
                        cols[0].style.backgroundColor = greenColor; //899E8B 99C5B5 9FAF90
                        cols[0].style.borderRadius = '10px';
                        cols[0].style.textAlign = 'center';
                        cols[0].style.color = '#fff';
                        cols[1].innerText = orderBookData.bids[i].amount.toFixed(decimals);
                        cols[2].innerText = ((cols[0].innerText * cols[1].innerText).toFixed(6)).toString();
                    }
                    else {
                        cols[0].innerText = "";
                        cols[0].style.backgroundColor = 'transparent';
                        cols[1].innerText = "";
                        cols[2].innerText = "";
                    }
                }
            })
            .catch(err => console.log(err))
    }

    const setChartData = () => {
        fetch(`${API_URL}/chain`)
            .then(res => res.json())
            .then(data => {
                data.chain.shift();
                setDataToOrdersHistoryTable(data);
                const cdata = data.chain.map(block => {
                    let filteredTransactions = block.transactions.filter(transaction => {
                        return (transaction.tradeTxId !== null) && (transaction.contract === firstCryptocurrency.toLowerCase());
                    })
                    let prices = filteredTransactions.map(transaction => {
                        return transaction.price;
                    })
                    let volume = filteredTransactions.map(transaction => {
                        return transaction.sendAmount;
                    })
                    return {time: new Date(block.timestamp * 1000).getTime(), prices: prices, volume: volume}
                })

                let currentDate = new Date();
                let minutes = (Math.ceil(currentDate.getMinutes() /interval) * interval) % 60;
                if (minutes === 0) {
                    let hours = Math.ceil(interval / 60);
                    currentDate.setHours(currentDate.getHours() + hours);
                }
                currentDate.setMinutes(minutes);
                currentDate.setSeconds(0);
                currentDate.setMilliseconds(0);
                let intervalStart = new Date(currentDate);
                intervalStart.setMinutes(intervalStart.getMinutes() - interval);
                let filteredData = cdata.filter(element => {
                    return element.time < intervalStart.getTime() && element.prices.length !== 0 && element.volume.length !== 0
                })

                let intervalEnd = new Date(intervalStart);
                intervalStart.setMinutes(intervalStart.getMinutes() - interval);
                let reversedFilteredData = filteredData.reverse();
                console.log(reversedFilteredData);
                let history = [[]];

                let i = 0;
                let j = 0;
                history[i].push(new Date(intervalStart));
                while (j < reversedFilteredData.length) {
                    let item = reversedFilteredData[j];
                    if (item.time >= intervalStart.getTime() && item.time < intervalEnd.getTime())
                    {
                        if (history[i].length === 0) {
                            history[i].push(new Date(intervalStart));
                        }
                        history[i].push(item);
                        j++;
                    }
                    else if (item.time < intervalStart.getTime()) {
                        intervalEnd = new Date(intervalStart);
                        intervalStart.setMinutes(intervalStart.getMinutes() - interval);
                        history.push([]);
                        i++;
                        history[i].push(new Date(intervalStart));
                    }
                }

                let candleSeriesHistoryData = [];
                let volumeSeriesHistoryData = [];

                history.forEach(item => {
                    let timestamp = new Date(item[0]);
                    if (item.length > 1) {
                        item.shift()
                        let close = item[0].prices[0];
                        let lastTransaction = item[item.length - 1];
                        let open = lastTransaction.prices[lastTransaction.prices.length - 1];
                        let high = null;
                        let low = null;
                        let totalVolume = null;

                        item.forEach(element => {
                            element.prices.forEach(price => {
                                if (low === null || price < low) low = price;
                                if (high === null || price > high) high = price;
                            })
                        })
                        item.forEach(element => {
                            element.volume.forEach(v => {
                                totalVolume += v;
                            })
                        })

                        candleSeriesHistoryData.push({time: timestamp.getTime() / 1000, open: open, high: high, low: low, close: close})
                        volumeSeriesHistoryData.push({time: timestamp.getTime() / 1000, value: totalVolume});
                    } else {
                        candleSeriesHistoryData.push({time: timestamp.getTime() / 1000, open: NaN, high: NaN, low: NaN, close: NaN})
                        volumeSeriesHistoryData.push({time: timestamp.getTime() / 1000, value: 0});
                    }
                })

                candleSeries.setData(candleSeriesHistoryData.reverse());
                volumeSeries.setData(volumeSeriesHistoryData.reverse());
            })
            .catch(err => console.log(err))
    }

    const updateChartData = () => {
        fetch(`${API_URL}/chain`)
            .then(res => res.json())
            .then(data => {
                data.chain.shift();
                setDataToOrdersHistoryTable(data);
                const cdata = data.chain.map(block => {
                    let filteredTransactions = block.transactions.filter(transaction => {
                        return (transaction.tradeTxId !== null) && (transaction.contract === firstCryptocurrency.toLowerCase());
                    })
                    let prices = filteredTransactions.map(transaction => {
                        return transaction.price;
                    })
                    let volume = filteredTransactions.map(transaction => {
                        return transaction.sendAmount;
                    })
                    return {time: new Date(block.timestamp * 1000).getTime(), prices: prices, volume: volume}
                })

                let currentDate = new Date();
                let minutes = (Math.ceil(currentDate.getMinutes() /interval) * interval) % 60;
                if (minutes === 0) {
                    let hours = Math.ceil(interval / 60);
                    currentDate.setHours(currentDate.getHours() + hours);
                }
                currentDate.setMinutes(minutes);
                currentDate.setSeconds(0);
                currentDate.setMilliseconds(0);
                let intervalStart = new Date(currentDate);
                intervalStart.setMinutes(intervalStart.getMinutes() - interval); // One day interval
                let filteredData = cdata.filter(element => {
                    return element.time >= intervalStart.getTime() && element.time < currentDate.getTime() && element.prices.length !== 0 && element.volume.length !== 0
                })
                if (filteredData.length !== 0) {
                    let open = filteredData[0].prices[0];
                    let lastTransaction = filteredData[filteredData.length - 1];
                    let close = lastTransaction.prices[lastTransaction.prices.length - 1];
                    let high = null;
                    let low = null;
                    let totalVolume = 0;

                    filteredData.forEach(element => {
                        element.prices.forEach(price => {
                            if (low === null || price < low) low = price;
                            if (high === null || price > high) high = price;
                        })
                    })
                    filteredData.forEach(element => {
                        element.volume.forEach(v => {
                            totalVolume += v;
                        })
                    })
                    let currentData = {time: intervalStart.getTime() / 1000, open: open, high: high, low: low, close: close};
                    candleSeries.update(currentData);
                    let currentDataVolume = {time: intervalStart.getTime() / 1000, value: totalVolume};
                    volumeSeries.update(currentDataVolume);
                }
                else {
                    let currentData = {time: intervalStart.getTime() / 1000, open: NaN, high: NaN, low: NaN, close: NaN};
                    candleSeries.update(currentData);
                    let currentDataVolume = {time: intervalStart.getTime() / 1000, value: NaN};
                    volumeSeries.update(currentDataVolume);
                }
            })
            .catch(err => console.log(err))
    }

    let refreshChart = setInterval(updateChartData, 5000);
    let refreshOrderBook = setInterval(orderBook, 5000);

    $btn.onclick = async () => {
        const price = parseFloat($priceInput.value.replace(',', '.'));
        const amountCalc = parseFloat($amountInput.value.replace(',', '.'));

        const amount = tradeDirection === TRADE_DIRECTIONS.SELL ? amountCalc : amountCalc * price;

        if (price === 0 || isNaN(price)) {
            setMessageToButton("Пожалуйста, введите цену", "Please input price", $error, $btn, $btnText);
            setTimeout(returnOldButton, 2000);
            return;
        }
        if (amount === 0 || isNaN(amountCalc)) {
            setMessageToButton("Пожалуйста, введите количество", "Please input amount", $error, $btn, $btnText);
            setTimeout(returnOldButton, 2000);
            return;
        }

        const currentSymbols = currentCryptocurrencyPair.toLowerCase();
        const symbolsArray = currentSymbols.split('/');
        const symbolToSend = tradeDirection === TRADE_DIRECTIONS.BUY ? symbolsArray[1] : symbolsArray[0]
        const symbolToGet = tradeDirection === TRADE_DIRECTIONS.BUY ? symbolsArray[0] : symbolsArray[1]

        // if (balances === [])
        // {
        //     setMessageToButton('Ошибка. Не удалось загрузить данные о балансе. Пожалуйста, повторите попытку позже.')
        //     return;
        // }

        let tokenBalance = balances.filter(item => item.token === symbolToSend.toUpperCase())[0];

        if (tokenBalance !== undefined && amount > tokenBalance.balance) {
            setMessageToButton("Недостаточно средств", "Insufficient funds", $error, $btn, $btnText);
            setTimeout(returnOldButton, 2000);
            return;
        }

        let walletAddress = localStorage.getItem('walletAddress');
        if (walletAddress === null) {
            $accButtons.style.display = "none";
            $authButtons.style.display = "flex";
            showAuthError();
            return;
        }
        let tx = {
            'type': 'trade',
            'sender': walletAddress,
            'symbol': currentSymbols,
            price,
            'send': symbolToSend,
            'sendVol': amount,
            'get': symbolToGet,
            'getVol': tradeDirection === TRADE_DIRECTIONS.BUY ? amount / price : price * amount,
            'comissionAmount': 2,
        }
        try {
            showLoader();
            let result = await postData(`${API_URL}/transactions/new`, tx);
            hideLoader();
            let data = await result.json();
            if (data.MSG) {
                if (data.MSG.includes("Tx pool synced among")) {
                    setMessageToButton("Заявка отправлена", "Application has been sent", $success, $btn, $btnText);
                    $priceInput.value = '';
                    $amountInput.value = '';
                    $totalPrice.innerText = '';
                    await setBalance();
                } else if (data.MSG.includes("Try to sign in first"))
                    showAuthError();
                else if (data.MSG.includes("Spend amount exceeds account balance"))
                    setMessageToButton("Недостаточно средств", "Insufficient funds", $error, $btn, $btnText);
                else {
                    setMessageToButton("Ошибка на сервере. Пожалуйста, повторите попытку позже.", "Server error. Please try again later", $error, $btn, $btnText);
                }
            } else {
                setMessageToButton("Ошибка на сервере. Пожалуйста, повторите попытку позже.", "Server error. Please try again later", $error, $btn, $btnText);
            }
        } catch (e) {
            hideLoader();
            setMessageToButton("Ошибка на сервере. Пожалуйста, повторите попытку позже.", "Server error. Please try again later", $error, $btn, $btnText);
        }
        setTimeout(returnOldButton, 2000);
    }

    const postData = async (url = '', data = {}) => {
        const response = await fetch(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        return response;
    }

    const showLoader = () => {
        $btnText.style.display = "none";
        $sendBtnText.style.display = "none";
        $btn.style.pointerEvents = "none";
        $sendBtn.style.pointerEvents = "none";
        $loader.style.display = "block";
        $loader2.style.display = "block";
    }

    const hideLoader = () => {
        $btn.style.background = $primaryColor;
        $sendBtn.style.background = $primaryColor;
        $loader.style.display = "none";
        $loader2.style.display = "none";
        $btnText.style.display = "block";
        $sendBtnText.style.display = "block";
    }

    const setMessageToButton = (russianMessage, englishMessage, backgroundColor = $primaryColor, button, buttonText) => {
        language = localStorage.getItem('language');
        button.style.background = backgroundColor;
        button.style.pointerEvents = "none";
        if (language === "rus" || language === null)
            buttonText.innerText = russianMessage;
        else
            buttonText.innerText = englishMessage;
    }

    const showAuthError = () => {
        $totalPriceField.style.display = "none";
        $totalAndBtnWrapper.style.height = "80px";
        $totalAndBtnWrapper.style.justifyContent = "center";
        $btn.style.pointerEvents = "none";
        $sendBtn.style.pointerEvents = "none"
        $btn.style.display = "none";
        $sendBtn.style.display = "none";
        $authError.style.display = "flex";
        $authErrorSecondTab.style.display = "flex";
    }

    const returnOldButton = () => {
        $btn.style.pointerEvents = "auto";
        $btn.style.removeProperty("background");
        $sendBtn.style.pointerEvents = "auto";
        $sendBtn.style.removeProperty("background");
        tradeDirection === TRADE_DIRECTIONS.SELL ? setPhraseLanguage($btnText, `Продать ${firstCryptocurrency}`, `Sell ${firstCryptocurrency}`)
            : setPhraseLanguage($btnText, `Купить ${firstCryptocurrency}`, `Buy ${firstCryptocurrency}`);
        setPhraseLanguage($sendBtnText, 'Отправить ZSH', 'Send ZSH')
    }

    $exitBtn.onclick = async () => {
        try {
            let result = await fetch(`${API_URL}/wallet/logout`);
            let data = await result.json();
            if (data.MSG)
                if (data.MSG === true)
                    console.log('success')
        }
        catch (e){
            console.log(e);
        }
        localStorage.removeItem("walletAddress");
        $accButtons.style.display = "none";
        $authButtons.style.display = "flex";
        showAuthError();
    }

    const getShortAddress = () => {
        let walletAddress = localStorage.getItem('walletAddress');
        let addressLength = walletAddress.length;
        return `${walletAddress.slice(0, 4)}...${walletAddress.slice(addressLength - 4, addressLength)}`
    }

    $copyIcon.onclick = async () => {
        let copyText = localStorage.getItem('walletAddress');
        await navigator.clipboard.writeText(copyText)
        $copyMessage.style.opacity = "1";
        setTimeout(() => {
            $copyMessage.style.opacity = "0";
        }, 1000)
    }

    $accButton.onclick = () => {
        $accButton.style.borderBottomColor = 'white';
        if ($accountWrapper.style.opacity === "" || $accountWrapper.style.opacity === "0")
            $accountWrapper.style.opacity = "1.0";
        else $accountWrapper.style.opacity = "0";
    }

    $sendBtn.onclick = async () => {
        const recipient = $recipientInput.value;
        const amount = parseFloat($zshAmountInput.value.replace(',','.'));

        if (recipient.length === 0) {
            setMessageToButton("Пожалуйста, укажите адрес получателя", "Please input recipient's address", $error, $sendBtn, $sendBtnText);
            setTimeout(returnOldButton, 2000);
            return;
        }
        if (amount === 0 || isNaN(amount)) {
            setMessageToButton("Введите количество", "Please input amount", $error, $sendBtn, $sendBtnText);
            setTimeout(returnOldButton, 2000);
            return;
        }

        // if (balances === [])
        // {
        //     setMessageToButton('Ошибка. Не удалось загрузить данные о балансе. Пожалуйста, повторите попытку позже.')
        //     return;
        // }

        let tokenBalance = balances.filter(item => item.token === 'ZSH')[0];

        if (tokenBalance !== undefined && amount > tokenBalance.balance) {
            setMessageToButton("Недостаточно средств", "Insufficient funds", $error, $sendBtn, $sendBtnText);
            setTimeout(returnOldButton, 2000);
            return;
        }

        let walletAddress = localStorage.getItem('walletAddress');
        if (walletAddress === null) {
            $accButtons.style.display = "none";
            $authButtons.style.display = "flex";
            showAuthError();
            return;
        }


        let tx = {
            'type': 'common',
            'symbol': 'zsh',
            'contract': null,
            'sender': walletAddress,
            'recipient': $recipientInput.value,
            'sendAmount': amount,
            'comissionAmount': 2,
        }
        try {
            showLoader();
            let result = await postData(`${API_URL}/transactions/new`, tx);
            hideLoader();
            let data = await result.json();

            if (data.MSG) {
                if (data.MSG.includes("Tx pool synced among")) {
                    setMessageToButton("Заявка отправлена", "Application has been sent", $success, $sendBtn, $sendBtnText);
                    $recipientInput.value = '';
                    $zshAmountInput.value = '';
                    await setBalance();
                } else if (data.MSG.includes("Try to sign in first"))
                    showAuthError();
                else if (data.MSG.includes("Spend amount exceeds account balance"))
                    setMessageToButton("Недостаточно средств", "Insufficient funds", $error, $sendBtn, $sendBtnText);
                else {
                    setMessageToButton("Ошибка на сервере. Пожалуйста, повторите попытку позже.", "Server error. Please try again later", $error, $sendBtn, $sendBtnText);
                }
            } else {
                setMessageToButton("Ошибка на сервере. Пожалуйста, повторите попытку позже.", "Server error. Please try again later", $error, $sendBtn, $sendBtnText);
            }
        } catch (e) {
            hideLoader();
            setMessageToButton("Ошибка на сервере. Пожалуйста, повторите попытку позже.", "Server error. Please try again later", $error, $sendBtn, $sendBtnText);
        }
        setTimeout(returnOldButton, 2000);
    }
})
