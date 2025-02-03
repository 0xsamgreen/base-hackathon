import { createWalletClient, http, parseEther } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { baseSepolia } from 'viem/chains';
import * as crypto from 'crypto';
import * as dotenv from 'dotenv';
dotenv.config();
const transport = http(process.env.BASE_SEPOLIA_RPC_URL);
export class WalletService {
    async createWallet() {
        // Generate random private key
        const privateKey = crypto.randomBytes(32).toString('hex');
        const account = privateKeyToAccount(`0x${privateKey}`);
        // Create wallet client to verify it works
        const client = createWalletClient({
            account,
            chain: baseSepolia,
            transport: http()
        });
        // Get address to verify wallet works
        const address = account.address;
        return {
            address,
            privateKey
        };
    }
    async getWalletClient(privateKey) {
        // Create account from private key
        const account = privateKeyToAccount(`0x${privateKey}`);
        // Create and return wallet client
        return createWalletClient({
            account,
            chain: baseSepolia,
            transport: http()
        });
    }
    async sendTransaction(privateKey, to, amount) {
        const account = privateKeyToAccount(`0x${privateKey}`);
        const client = createWalletClient({
            account,
            chain: baseSepolia,
            transport
        });
        const hash = await client.sendTransaction({
            account,
            chain: baseSepolia,
            to: to,
            value: parseEther(amount),
            kzg: undefined // Required by viem v2 but not needed for Base
        });
        return hash;
    }
}
