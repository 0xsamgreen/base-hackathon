#!/usr/bin/env node

import { WalletService } from './wallet.js';
import { createPublicClient, http, formatEther } from 'viem';
import { baseSepolia } from 'viem/chains';

const method = process.argv[2];
const args = process.argv.slice(3);
const service = new WalletService();

try {
    let result;
    switch (method) {
        case 'createWallet':
            result = await service.createWallet();
            break;
        case 'getWalletClient':
            const client = await service.getWalletClient(args[0]);
            const publicClient = createPublicClient({
                chain: baseSepolia,
                transport: http()
            });
            const balance = await publicClient.getBalance({
                address: client.account.address
            });
            result = {
                address: client.account.address,
                balance: formatEther(balance)
            };
            break;
        case 'sendTransaction':
            result = await service.sendTransaction(args[0], args[1], args[2]);
            break;
        default:
            throw new Error(`Unknown method: ${method}`);
    }
    console.log(JSON.stringify(result));
} catch (error) {
    console.error(error);
    process.exit(1);
}
