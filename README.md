# Zanshin Exchange
Zanshin is a decentralised exchange for exchanging digital assets.  
Zanshin provides users with the security of DEX applications, while providing the full functionality of centralised exchanges, including but not limited to the following features:  
- various types of trade orders: market, limit orders and their variations;  
- high speed of execution of trade orders;  
- margin trading;  
- pooling and staking.  

The project is implemented on the basis of its own blockchain, a distinctive feature of which is the attribution of transactions. Each transaction sent to the network contains all the information necessary to identify the type of order. Depending on the configuration of the filled-in transaction fields, Zanshin determines whether the latter belongs to one of the transaction pools: common pool or trade pool.  
The trade pool contains all limit trading orders. As soon as a counter order is found for a specific trade order that satisfies the conditions for exchanging the first order, the Zanshin Virtual Machine (ZVM) generates outgoing transactions based on the conditions of these two orders and sends them to the common pool.  
The common pool contains transactions for the transfer of the native Zanshin token, as well as outgoing transactions from the trade pool.  
Transactions from the common pool are considered completed as soon as they turn on the next block found during mining on the Zanshin network.  
The Zanshin network supports several kinds of nodes:  
- Full node - combines all available functions: mining, matching (by means of ZVM), synchronisation of pools and chains, key storage, custom API;  
- Custom Node - Contains blockchain replica, key-store, and custom API.  
The extensive system of rights provided by such a network configuration allows achieving high transaction speed with low commission costs. Anyone can install a specific type of node (s) based on their own needs and goals.  

NB! Project is in its early prototype stage. There is still a lot of work ahead!  

## Prototype Testing  

To test project you would like to:
1. Clone GitHub repository;  
2. Go to projects folder and install all dependencies with requirements.txt;  
3. Run Zanshin node by running command: python blockchainApi.py;  
4. Create second node instance by going to node1 folder inside the projects folder and running command: python blockchainApi.py;  
5. Run http://localhost:5000 in your browser;  
6. Create an account with Sign up procedure in your browser;  
7. Start mining process by going to bots folder in the projects root folder and running command: python miner.py http//localhost:5000  

Your account will be starting to credited by projects native tokens (ZSH). To see your current ZSH balance refresh your browsers window.  

To start trading process lead following steps.  
1. Create additional account on http//localhost:5000 node by following Sign up procedure. Use different password;  
2. Run jupyter notebook in projects root folder. Open dexFuncTest1.ipynb. Run first and second cells. Your accounts will be automatically credited by 1'000'000 test USDT;  
3. Copy your seconds account address (you can find it in "My Account"), Log out and Log In to your first account;  
4. Send some ZSH from you first account to your second account ("Send ZSH" tab -> paste your seconds account address -> specify ZSH amount to be send; around 100 is recommended -> press "Send ZSH");  
5. Open two new terminal windows and go to bots folder in projects root folder in each of windows;  
6. Run first trader bot by executing following command in the first terminal window: python trader1.py [your first accounts address] http://localhost:5000  
7. Run second trader bot by executing following command in the second terminal window: python trader2.py [your second accounts address] http://localhost:5000  
  
It will run the test trading process.
