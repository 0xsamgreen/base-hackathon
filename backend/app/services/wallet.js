const { createWalletClient, http, parseEther } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { baseSepolia } = require('viem/chains');
const crypto = require('crypto');

class WalletService {
    async createWallet() {
        const privateKey = crypto.randomBytes(32).toString('hex');
        const account = privateKeyToAccount(`0x${privateKey}`);
        const client = createWalletClient({
            account,
            chain: baseSepolia,
            transport: http()
        });
        const address = account.address;
        return {
            address,
            privateKey
        };
    }

    async getWalletClient(privateKey) {
        const account = privateKeyToAccount(`0x${privateKey}`);
        return createWalletClient({
            account,
            chain: baseSepolia,
            transport: http()
        });
    }

    async sendTransaction(privateKey, to, amount) {
        const account = privateKeyToAccount(`0x${privateKey}`);
        const client = await this.getWalletClient(privateKey);
        const hash = await client.sendTransaction({
            account,
            chain: baseSepolia,
            to,
            value: parseEther(amount),
            kzg: undefined // Required by viem v2 but not needed for Base
        });
        return hash;
    }
}

module.exports = { WalletService };
