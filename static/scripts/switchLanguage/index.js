$(function () {
    const $ruLanguageBtn = document.getElementById('ru-language-btn');
    const $enLanguageBtn = document.getElementById('en-language-btn');

    window.addEventListener("load", async function (event) {
        if (localStorage.getItem('language') === null)
            setLanguage('rus');
        else
            setLanguage(localStorage.getItem('language'))
    })

    const languages = {
        "rus": {
            loginBtnTitle: "Вход",
            registerBtnTitle: "Регистрация",
            accountBtnTitle: "Мой аккаунт",
            exitBtnTitle: "Выход",
            copyMessage: "Адрес скопирован в буфер обмена",
            assetsListTitle: "Активы",
            limitOrderBtnTitle: "Лимитный ордер",
            sendZshBtnTitle: "Отправить ZSH",
            priceFieldLabel: "Цена",
            amountFieldLabel: "Количество",
            totalPriceFieldLabel: "Всего",
            authErrorLogin: "Войдите",
            authErrorOr: "или",
            authErrorRegister: "Зарегистрируйтесь",
            recipientFieldLabel: "Получатель",
            recipientFieldPlaceholder: "Введите адрес получателя",
            commissionInfo: "Комиссия (0,01%): 0 ZSH",
            orderBookTablePriceColumn: "Цена(USDT)",
            orderBookTableAmountColumn: "Количество(ZSH)",
            orderBookTableTotalColumn: "Всего",
            openOrdersTabTitle: "Открытые сделки",
            ordersHistoryTabTitle: "История сделок",
            openOrdersTableHead: ["Дата","Пара","Тип","Направление","Цена","Количество"],
            openOrdersInfo: "У вас пока нет открытых сделок",
            ordersHistoryTableHead: ["Дата","Пара","Тип","Направление","Цена","Количество","Статус"],
            ordersHistoryInfo: "У вас пока нет истории сделок",
            toggleButtonBuy: "Купить",
            toggleButtonSell: "Продать",
            buyZshBtnTitle: "Купить ZSH",
            sellZshBtnTitle: "Продать ZSH",
        },
        "eng": {
            loginBtnTitle: "Log In",
            registerBtnTitle: "Sign up",
            accountBtnTitle: "My account",
            exitBtnTitle: "Log Out",
            copyMessage: "Address copied to clipboard",
            assetsListTitle: "Assets",
            limitOrderBtnTitle: "Limit Order",
            sendZshBtnTitle: "Send ZSH",
            priceFieldLabel: "Price",
            amountFieldLabel: "Amount",
            totalPriceFieldLabel: "Total",
            authErrorLogin: "Log In",
            authErrorOr: "or",
            authErrorRegister: "Sign up",
            recipientFieldLabel: "Recipient",
            recipientFieldPlaceholder: "Input recipient's address",
            commissionInfo: "Commission (0,01%): 0 ZSH",
            orderBookTablePriceColumn: "Price(USDT)",
            orderBookTableAmountColumn: "Amount(ZSH)",
            orderBookTableTotalColumn: "Total",
            openOrdersTabTitle: "Open orders",
            ordersHistoryTabTitle: "Orders history",
            openOrdersTableHead: ["Date","Pair","Type","Direction","Price","Amount"],
            openOrdersInfo: "You have no open orders yet",
            ordersHistoryTableHead: ["Date","Pair","Type","Direction","Price","Amount","Status"],
            ordersHistoryInfo: "You have no orders history yet",
            toggleButtonBuy: "Buy",
            toggleButtonSell: "Sell",
            buyZshBtnTitle: "Buy ZSH",
            sellZshBtnTitle: "Sell ZSH",
        }
    }

    const setLanguage = (language) => {
        if (language === 'rus') {
            $ruLanguageBtn.style.backgroundColor = 'rgba(255,255,255,0.2)';
            $enLanguageBtn.style.backgroundColor = 'transparent';
        }
        else {
            $enLanguageBtn.style.backgroundColor = 'rgba(255,255,255,0.2)';
            $ruLanguageBtn.style.backgroundColor = 'transparent';
        }
        localStorage.setItem('language', language);
        document.getElementById('login-btn-title').innerText = languages[language].loginBtnTitle;
        document.getElementById('register-btn-title').innerText = languages[language].registerBtnTitle;
        document.getElementById('acc-btn').innerText = languages[language].accountBtnTitle;
        document.getElementById('exit-btn').innerText = languages[language].exitBtnTitle;
        document.getElementById('copy-message').innerText = languages[language].copyMessage;
        document.getElementById('tokens-list-title').innerText = languages[language].assetsListTitle;
        document.getElementById('limit-order-btn').innerText = languages[language].limitOrderBtnTitle;
        document.getElementById('send-zsh-btn').innerText = languages[language].sendZshBtnTitle;
        document.getElementById('price-field').innerText = languages[language].priceFieldLabel;
        document.getElementById('amount-field').innerText = languages[language].amountFieldLabel;
        document.getElementById('total-price-field-title').innerText = languages[language].totalPriceFieldLabel;
        document.getElementById('auth-error-login').innerText = languages[language].authErrorLogin;
        document.getElementById('btn-text2').innerText = languages[language].authErrorOr;
        document.getElementById('auth-error-register').innerText = languages[language].authErrorRegister;
        document.getElementById('recipient-field').innerText = languages[language].recipientFieldLabel;
        document.getElementById('recipient-input').placeholder = languages[language].recipientFieldPlaceholder;
        document.getElementById('amount-field-SZ').innerText = languages[language].amountFieldLabel;
        document.getElementById('commission-info').innerText = languages[language].commissionInfo;
        document.getElementById('send-btn-text').innerText = languages[language].sendZshBtnTitle;
        document.getElementById('auth-error-login-SZ').innerText = languages[language].authErrorLogin;
        document.getElementById('auth-error-or-SZ').innerText = languages[language].authErrorOr;
        document.getElementById('auth-error-register-SZ').innerText = languages[language].authErrorRegister;
        document.getElementById('table-price-col-1').innerText = languages[language].orderBookTablePriceColumn;
        document.getElementById('table-amount-col-1').innerText = languages[language].orderBookTableAmountColumn;
        document.getElementById('table-total-col-1').innerText = languages[language].orderBookTableTotalColumn;
        document.getElementById('table-price-col-2').innerText = languages[language].orderBookTablePriceColumn;
        document.getElementById('table-amount-col-2').innerText = languages[language].orderBookTableAmountColumn;
        document.getElementById('table-total-col-2').innerText = languages[language].orderBookTableTotalColumn;
        document.getElementById('open-orders-btn').innerText = languages[language].openOrdersTabTitle;
        document.getElementById('orders-history-btn').innerText = languages[language].ordersHistoryTabTitle;
        let openOrdersTableHead = document.getElementById('open-orders-table-head').getElementsByTagName('th');
        for (let i = 0; i < openOrdersTableHead.length; i++ )
            openOrdersTableHead[i].innerText = languages[language].openOrdersTableHead[i];
        let ordersHistoryTableHead = document.getElementById('orders-history-table-head').getElementsByTagName('th');
        for (let i = 0; i < ordersHistoryTableHead.length; i++ )
            ordersHistoryTableHead[i].innerText = languages[language].ordersHistoryTableHead[i];
        document.getElementById('open-orders-info').innerText = languages[language].openOrdersInfo;
        document.getElementById('orders-history-info').innerText = languages[language].ordersHistoryInfo;
        document.querySelector('.toggle-button input').setAttribute('toggle-btn-content-before', languages[language].toggleButtonBuy);
        document.querySelector('.toggle-button input').setAttribute('toggle-btn-content-after', languages[language].toggleButtonSell);
        if ($('#switch').prop('checked')) {
            document.getElementById('btn-text').innerText = languages[language].sellZshBtnTitle;
        } else {
            document.getElementById('btn-text').innerText = languages[language].buyZshBtnTitle;
        }

    }

    $ruLanguageBtn.onclick = () => {
        setLanguage('rus');
    }

    $enLanguageBtn.onclick = () => {
        setLanguage('eng');
    }
})
