const { WalletService } = require('./app/services/wallet_wrapper');

async function test() {
  const wallet = new WalletService();
  
  try {
    console.log('Creating wallet...');
    const result = await wallet.createWallet();
    console.log('Created wallet:', result);
  } catch (error) {
    console.error('Error:', error);
  }
}

test();
