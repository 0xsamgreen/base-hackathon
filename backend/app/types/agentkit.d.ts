declare module 'agentkit' {
    export interface AgentConfig {
        client: any;
        chain: any;
    }

    export class Agent {
        constructor(config: AgentConfig);
        
        client: any;
        
        deployNFTContract(params: {
            name: string;
            symbol: string;
            baseTokenURI?: string;
        }): Promise<{
            contractAddress: `0x${string}`;
            transactionHash: string;
        }>;
        
        mintNFT(params: {
            to: string;
            metadata: {
                name: string;
                description: string;
                image: string;
                attributes: any;
            };
            contractAddress: `0x${string}`;
        }): Promise<{
            tokenId: bigint;
            transactionHash: string;
        }>;

        getTokenURI(params: {
            tokenId: bigint;
            contractAddress: `0x${string}`;
        }): Promise<string>;
    }
}
