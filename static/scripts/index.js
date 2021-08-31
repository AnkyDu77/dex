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

    const API_URL = 'http://0.0.0.0:5000'; //Alina http://178.176.120.241:5002
    //const API_URL = 'http://4a9b-77-222-104-154.ngrok.io';
    const TRADE_DIRECTIONS = {SELL: 'SELL', BUY: 'BUY'};
    let tradeDirection = TRADE_DIRECTIONS.BUY;

    const $primaryColor = "#4C5C97"
    const $error = "#E27B7B";
    const $success = "#9FAF90";

    const cryptocurrencyPairs = ['ZSH/USDT', 'BTC/USDT', 'BTC/DAI', 'ETH/USDT', 'ETH/DAI', 'BNB/USDT', 'BNB/DAI', 'DOT/USDT',
        'DOT/DAI', 'UNI/USDT', 'UNI/DAI', 'BTC/ETH', 'ETH/UNI', 'BTC/DOT', 'ETH/DOT']

    const defaultCryptocurrencyPair = 'ZSH/USDT';
    let currentCryptocurrencyPair = defaultCryptocurrencyPair;
    let firstCryptocurrency = defaultCryptocurrencyPair.substring(0, defaultCryptocurrencyPair.indexOf('/'));
    let secondCryptocurrency = defaultCryptocurrencyPair.substring(defaultCryptocurrencyPair.indexOf('/') + 1,
        defaultCryptocurrencyPair.length);
    let balances = [];

    const setCryptocurrency = (currentPair) => {
        $currentPairLabel.innerText = currentPair;
        currentCryptocurrencyPair = currentPair;
        firstCryptocurrency = currentCryptocurrencyPair.substring(0, currentCryptocurrencyPair.indexOf('/'));
        secondCryptocurrency = currentCryptocurrencyPair.substring(currentCryptocurrencyPair.indexOf('/') + 1,
            currentCryptocurrencyPair.length);


        if ($('#switch').prop('checked')) $btnText.innerText = `Продать ${firstCryptocurrency}`;
        else $btnText.innerText = `Купить ${firstCryptocurrency}`;
        $secondCryptocurrencyLabel.innerText = secondCryptocurrency;
        $firstCryptocurrencyLabel.innerText = firstCryptocurrency;
        $totalCryptocurrencyLabel.innerText = secondCryptocurrency;

        $tablePriceCol1.innerText = `Цена (${secondCryptocurrency})`;
        $tableAmountCol1.innerText = `Количество (${firstCryptocurrency})`;
        $tablePriceCol2.innerText = `Цена (${secondCryptocurrency})`;
        $tableAmountCol2.innerText = `Количество (${firstCryptocurrency})`;

        // setChartData();
    }

    window.addEventListener("load", async function (event) {
        makeList();
        createTable($asksTable);
        createTable($bidsTable);
        setCryptocurrency(defaultCryptocurrencyPair);
        // setChartData();
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
    }, false);

    window.addEventListener("mousedown", async function (event) {
        let $accountWindow = document.getElementById('account-window-with-triangle');
        if (event.target !== $accountWindow && !$accountWindow.contains(event.target) && $accountWrapper.style.opacity === "1") {
            $accountWrapper.style.opacity = "0";
            $accButton.style.borderBottomColor = 'transparent';
        }
    })

    $switchButton.onclick = () => {
        returnOldButton();
        if ($('#switch').prop('checked')) {
            $btnText.innerText = `Продать ${firstCryptocurrency}`;
            tradeDirection = TRADE_DIRECTIONS.SELL;
        } else {
            $btnText.innerText = `Купить ${firstCryptocurrency}`;
            tradeDirection = TRADE_DIRECTIONS.BUY;
        }
    }

    const decimals = 6;

    $priceInput.oninput = () => {
        returnOldButton();
        let price = Number($priceInput.value);
        $priceInput.value = Math.round((price) * 1000000) / 1000000;
        let amount = Number($amountInput.value);
        if (price > 0 && amount > 0) $totalPrice.innerText = (Math.round((price * amount) * 10 ** (decimals)) /
            10 ** (decimals)).toString().replace('.', ',');
    }

    $amountInput.oninput = () => {
        returnOldButton();
        let amount = Number($amountInput.value);
        $amountInput.value = Math.round(amount * 10 ** (decimals)) / 10 ** (decimals);
        let price = Number($priceInput.value);
        if (price > 0 && amount > 0) $totalPrice.innerText = (Math.round((price * amount) * 10 ** (decimals)) /
            10 ** (decimals)).toString().replace('.', ',');
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

    const setDataToOpenOrdersTable = (data) => {
        let walletAddress = localStorage.getItem('walletAddress');
        let filteredData = data.tradeOrders.filter(order => {
            return order.sender === walletAddress
        })
        let parsedData = filteredData.map(element => {
            let direction = null;
            let date = new Date(element.timestamp*1000)
            let formattedDate = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear() + ' '
                + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
            // first token && second token
            if (element.get === firstCryptocurrency.toLowerCase() && element.send === secondCryptocurrency.toLowerCase()) {
                direction = 'BUY';
            }
            // second token && first token
            if (element.get === secondCryptocurrency.toLowerCase() && element.send === firstCryptocurrency.toLowerCase()) {
                direction = 'SELL';
            }
            return [formattedDate, element.symbol.toUpperCase(), 'LIMIT', direction, element.price, parseFloat(element.sendVol).toFixed(6)]
        })

        let infoWrapper = document.getElementById('open-orders-info')
        if (filteredData.length > 0) {
            infoWrapper.style.display = 'none';
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
            let firstSymbol = pair.substring(0, pair.indexOf('/'));
            let secondSymbol = pair.substring(pair.indexOf('/') + 1, pair.length);
            let direction = null;
            let date = new Date(element.timestamp*1000)
            let formattedDate = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear() + ' '
                + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
            if (element.contract === firstSymbol) {
                direction = 'BUY';
            }
            if (element.contract === secondSymbol) {
                direction = 'SELL';
            }
            let status = 'DONE';
            return [formattedDate, element.symbol.toUpperCase(), 'LIMIT', direction, element.price, status]
        })

        let infoWrapper = document.getElementById('orders-history-info')
        if ( mergedData.length > 0) {
            infoWrapper.style.display = 'none';
            let ordersHistoryTable = document.getElementById('orders-history-table-body');
            ordersHistoryTable.innerHTML = "";
            for (let i = 0; i < mergedData.length; ++i) {
                let tableRow = document.createElement('tr');
                ordersHistoryTable.appendChild(tableRow);
                for (let j = 0; j < 6; ++j) {
                    if (j === 5 && parsedData[i][j] === 'DONE')
                    {
                        let tableCell = document.createElement('td');
                        tableRow.appendChild(tableCell);
                        let tableCellText = document.createElement('div');
                        tableCell.appendChild(tableCellText);
                        tableCellText.innerText = parsedData[i][j];
                        tableCellText.style.backgroundColor = '#9FAF90';
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
                        cols[0].style.backgroundColor = '#FB8387'; // F08CAE EA9EC7
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
                        cols[0].style.backgroundColor = '#9FAF90'; //899E8B 99C5B5 9FAF90
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

    // const setChartData = () => {
    //     fetch('https://api.binance.com/api/v3/klines?symbol=' + $currentPairLabel.innerText.replace('/', '') + '&interval=15m&limit=1000')
    //         .then(res => res.json())
    //                 .then(data => {
    //                     const cdata = data.map(d => {
    //                         return {time:d[0]/1000,open:parseFloat(d[1]),high:parseFloat(d[2]),low:parseFloat(d[3]),close:parseFloat(d[4])}
    //                     });
    //                     candleSeries.setData(cdata);
    //                 })
    //                 .catch(err => console.log(err))
    //     }

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
                let chartIntervalStart = new Date();
                chartIntervalStart.setDate(currentDate.getDate() - 7); // One day interval
                let filteredData = cdata.filter(element => {
                    return element.time > chartIntervalStart.getTime() && element.prices.length !== 0 && element.volume.length !== 0
                })
                if (filteredData.length !== 0) {
                    let open = filteredData[0].prices[0];
                    let lastTransaction = filteredData[filteredData.length - 1];
                    let lastPrice = lastTransaction.prices[lastTransaction.prices.length - 1];
                    let close = lastPrice;
                    let high = null;
                    let low = null;
                    let totalVolume = null;

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
                    currentDate.setHours(0);
                    currentDate.setMinutes(0);
                    currentDate.setSeconds(0);
                    currentDate.setMilliseconds(0);
                    let currentData = {time: currentDate.getTime() / 1000, open: open, high: high, low: low, close: close};
                    candleSeries.update(currentData);
                    let currentDataVolume = {time: currentDate.getTime() / 1000, value: totalVolume};
                    volumeSeries.update(currentDataVolume);
                }
            })
            .catch(err => console.log(err))
    }

    let refreshChart = setInterval(updateChartData, 5000);
    let refreshOrderBook = setInterval(orderBook, 5000);

    $btn.onclick = async () => {
        const price = parseFloat($priceInput.value);
        const amountCalc = parseFloat($amountInput.value);
        const amount = tradeDirection === TRADE_DIRECTIONS.SELL ? amountCalc : amountCalc * price;

        if (price === 0 || isNaN(price)) {
            setMessageToButton("Введите цену", $error);
            return;
        }
        if (amount === 0 || isNaN(amount)) {
            setMessageToButton("Введите количество", $error);
            return;
        }

        const currentSymbols = currentCryptocurrencyPair.toLowerCase();
        const symbolsArray = currentSymbols.split('/');
        const symbolToSend = tradeDirection === TRADE_DIRECTIONS.BUY ? symbolsArray[1] : symbolsArray[0]
        const symbolToGet = tradeDirection === TRADE_DIRECTIONS.BUY ? symbolsArray[0] : symbolsArray[1]
        let tokenBalance = balances.filter(item => item.token === symbolToSend.toUpperCase())[0];

        if (tokenBalance !== undefined && amount > tokenBalance.balance) {
            setMessageToButton("Недостаточно средств", $error);
            return;
        }

        let walletAddress = localStorage.getItem('walletAddress');
        if (walletAddress === null) {
            $accButtons.style.display = "none";
            $authButtons.style.display = "flex";
            showAuthError();
            return;
        }
        tx = {
            'type': 'trade',
            'sender': walletAddress,
            'symbol': currentSymbols,
            price,
            'send': symbolToSend,
            'sendVol': amount,
            'get': symbolToGet,
            'getVol': tradeDirection === TRADE_DIRECTIONS.BUY ? amount / price : price * amount,
            'comissionAmount': 2
        }
        try {
            showLoader();
            let result = await postData(`${API_URL}/transactions/new`, tx);
            hideLoader();
            let data = await result.json();
            if (data.MSG) {
                if (data.MSG.includes("Tx pool synced among")) {
                    setMessageToButton("Заявка отправлена", $success);
                    $priceInput.value = NaN;
                    $amountInput.value = NaN;
                    $totalPrice.innerText = '';
                    setBalance();
                } else if (data.MSG.includes("Try to sign in first"))
                    showAuthError();
                else if (data.MSG.includes("Spend amount exceeds account balance"))
                    setMessageToButton("Недостаточно средств", $error);
                else {
                    setMessageToButton("Ошибка на сервере. Пожалуйста повторите попытку позже.", $error);
                }
            } else {
                setMessageToButton("Ошибка на сервере. Пожалуйста повторите попытку позже.", $error);
            }
        } catch (e) {
            hideLoader();
            setMessageToButton("Ошибка на сервере. Пожалуйста повторите попытку позже.", $error);
        }
    }

    const postData = async (url = '', data = {}) => {
        const response = await fetch(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        return await response;
    }

    const showLoader = () => {
        $btnText.style.display = "none";
        $btn.style.pointerEvents = "none";
        $loader.style.display = "block";
    }

    const hideLoader = () => {
        $btn.style.background = $primaryColor;
        $loader.style.display = "none";
        $btnText.style.display = "block";
    }

    const setMessageToButton = (message, backgroundColor = $primaryColor) => {
        $btn.style.background = backgroundColor;
        $btn.style.pointerEvents = "none";
        $btnText.innerText = message;
    }

    const showAuthError = () => {
        $totalPriceField.style.display = "none";
        $totalAndBtnWrapper.style.height = "100px";
        $totalAndBtnWrapper.style.justifyContent = "center";
        $btn.style.pointerEvents = "none";
        $btn.style.display = "none";
        $authError.style.display = "flex";
    }

    const returnOldButton = () => {
        $btn.style.pointerEvents = "auto";
        $btn.style.removeProperty("background");
        $btnText.innerText = tradeDirection === TRADE_DIRECTIONS.SELL ? `Продать ${firstCryptocurrency}` : `Купить ${firstCryptocurrency}`;
    }

    $exitBtn.onclick = () => {
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
})
