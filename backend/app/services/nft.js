import { createWalletClient, http } from 'viem';
import { baseSepolia } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';
import { Agent } from 'agentkit';
import * as dotenv from 'dotenv';
dotenv.config();
const transport = http(process.env.BASE_SEPOLIA_RPC_URL);
export class NFTService {
    constructor() {
        const account = privateKeyToAccount(`0x${process.env.BACKEND_WALLET_PRIVATE_KEY}`);
        const client = createWalletClient({
            account,
            chain: baseSepolia,
            transport
        });
        this.agent = new Agent({
            client,
            chain: baseSepolia
        });
    }
    async mintNFT(recipientAddress, metadata) {
        try {
            // Convert attributes string to object
            const attributes = JSON.parse(metadata.attributes);
            // Create NFT metadata
            const tokenMetadata = {
                name: metadata.name,
                description: metadata.description,
                image: metadata.image_url,
                attributes
            };
            // Mint NFT using agentkit
            const result = await this.agent.mintNFT({
                to: recipientAddress,
                metadata: tokenMetadata,
                contractAddress: process.env.NFT_CONTRACT_ADDRESS
            });
            return {
                tokenId: result.tokenId,
                transactionHash: result.transactionHash
            };
        }
        catch (error) {
            console.error('Error minting NFT:', error);
            throw error;
        }
    }
    async getTokenURI(tokenId) {
        try {
            const uri = await this.agent.getTokenURI({
                tokenId,
                contractAddress: process.env.NFT_CONTRACT_ADDRESS
            });
            return uri;
        }
        catch (error) {
            console.error('Error getting token URI:', error);
            throw error;
        }
    }
}
