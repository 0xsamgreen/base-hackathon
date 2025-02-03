#!/usr/bin/env node
import { NFTService } from './nft.js';

async function main() {
    const command = process.argv[2];
    const service = new NFTService();

    try {
        switch (command) {
            case 'mint': {
                const recipientAddress = process.argv[3];
                const metadata = JSON.parse(process.argv[4]);
                const result = await service.mintNFT(recipientAddress, metadata);
                console.log(JSON.stringify(result));
                break;
            }
            case 'tokenUri': {
                const tokenId = BigInt(process.argv[3]);
                const uri = await service.getTokenURI(tokenId);
                console.log(uri);
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
