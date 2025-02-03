#!/usr/bin/env node
import { NFTDeployService } from './nft_deploy.js';

async function main() {
    const command = process.argv[2];
    const service = new NFTDeployService();

    try {
        switch (command) {
            case 'deploy': {
                const name = process.argv[3];
                const symbol = process.argv[4];
                const result = await service.deployNFTContract(name, symbol);
                console.log(JSON.stringify(result));
                break;
            }
            case 'verify': {
                const contractAddress = process.argv[3];
                const isValid = await service.verifyDeployment(contractAddress);
                console.log(JSON.stringify({ isValid }));
                break;
            }
            default:
                console.error('Unknown command:', command);
                process.exit(1);
        }
    } catch (error) {
        console.error(error.message);
        process.exit(1);
    }
}

main().catch(error => {
    console.error(error);
    process.exit(1);
});
